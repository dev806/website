"""
FastAPI Application Entry Point & Lifespan Assembly for [STUDIO_NAME]
Conforms to DOC-ARCH-001, DOC-ARCH-004, and DOC-ARCH-008.
"""

import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import Settings, get_settings
from app.database.connection import dispose_engine, get_engine
from app.routers import discovery_views, health, web
from app.modules.discovery import router as discovery_router
from app.shared.exceptions import AppException, format_error_response
from app.shared.logging import (
    configure_logging,
    correlation_id_ctx,
    get_logger,
)

logger = get_logger("app.main")

# Active state-changing public endpoints requiring IP rate limiting (5 req / 60 sec)
RATE_LIMITED_POST_ROUTES: Dict[str, tuple[int, int]] = {
    "/contact": (5, 60),
    "/discovery/start": (5, 60),
    "/discovery/problem": (5, 60),
    "/discovery/answers": (5, 60),
    "/discovery/unlock": (5, 60),
    "/discovery/review": (5, 60),
    "/discovery/backtrack": (5, 60),
}

# In-memory sliding-window store: IP -> Route Path -> list of timestamps (Process-Local)
_rate_limit_store: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))


def _get_client_ip(request: Request) -> str:
    """Extracts client IP address handling X-Forwarded-For safely."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def check_in_memory_rate_limit(client_ip: str, path: str) -> bool:
    """
    Process-local sliding-window rate limit checker.
    Returns True if request is allowed, False if rate limit exceeded.
    """
    if path not in RATE_LIMITED_POST_ROUTES:
        return True

    max_reqs, window_sec = RATE_LIMITED_POST_ROUTES[path]
    now = time.time()
    cutoff = now - window_sec

    timestamps = [ts for ts in _rate_limit_store[client_ip][path] if ts > cutoff]
    _rate_limit_store[client_ip][path] = timestamps

    if len(timestamps) >= max_reqs:
        return False

    _rate_limit_store[client_ip][path].append(now)
    return True



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager controlling resource allocation and release.
    Initializes database pools on startup and disposes them cleanly on shutdown.
    """
    settings = get_settings()
    configure_logging(
        level="DEBUG" if settings.debug else "INFO",
        json_format=(settings.app_env == "production"),
    )
    logger.info(f"Booting {settings.app_name} [env={settings.app_env}]")

    # Warm up engine singleton
    _ = get_engine(settings)

    yield

    logger.info(f"Shutting down {settings.app_name}")
    dispose_engine()


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """FastAPI application factory."""
    cfg = settings or get_settings()

    application = FastAPI(
        title=cfg.app_name,
        description="AI-native Technology Studio Platform",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if cfg.debug else None,
        redoc_url="/redoc" if cfg.debug else None,
    )

    # -------------------------------------------------------------------------
    # Middleware Registration Order (Starlette LIFO — last registered = outermost)
    # 1. Rate Limiting  (innermost — registered first)
    # 2. Security Headers (middle)
    # 3. Correlation ID   (outermost — registered last, wraps everything)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Middleware: Native In-Memory Rate Limiting (Phase 6.1)
    # -------------------------------------------------------------------------
    @application.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if request.method == "POST" and request.url.path in RATE_LIMITED_POST_ROUTES:
            client_ip = _get_client_ip(request)
            if not check_in_memory_rate_limit(client_ip, request.url.path):
                logger.warning(f"Rate limit exceeded for IP {client_ip} on path {request.url.path}")
                resp = format_error_response(
                    code="RATE_LIMIT_EXCEEDED",
                    message="Too many requests. Please try again later.",
                    details=[{"field": "ip", "issue": "Rate limit exceeded (maximum 5 requests per minute)."}],
                    request_id="",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )
                resp.headers["Retry-After"] = "60"
                return resp
        return await call_next(request)

    # -------------------------------------------------------------------------
    # Middleware: Native Security Headers (Phase 6.1)
    # -------------------------------------------------------------------------
    @application.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self';"
        )
        if cfg.app_env == "production" or request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # -------------------------------------------------------------------------
    # Middleware: Request Correlation ID (outermost — wraps all responses)
    # -------------------------------------------------------------------------
    @application.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        corr_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )
        token = correlation_id_ctx.set(corr_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = corr_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.debug(
                f"{request.method} {request.url.path} completed in {duration_ms}ms"
            )
            correlation_id_ctx.reset(token)


    # -------------------------------------------------------------------------
    # Exception Envelopes (DOC-ARCH-008)
    # -------------------------------------------------------------------------
    @application.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        logger.warning(f"Domain exception [{exc.code}]: {exc.message}")
        return format_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=req_id,
            status_code=exc.status_code,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        details = [
            {"field": ".".join(str(loc) for loc in err["loc"]), "issue": err["msg"]}
            for err in exc.errors()
        ]
        return format_error_response(
            code="VALIDATION_FAILED",
            message="Request parameters failed validation.",
            details=details,
            request_id=req_id,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        code = f"HTTP_{exc.status_code}"
        return format_error_response(
            code=code,
            message=str(exc.detail),
            request_id=req_id,
            status_code=exc.status_code,
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return format_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred.",
            request_id=req_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # -------------------------------------------------------------------------
    # Static Assets & Templates Mounting
    # -------------------------------------------------------------------------
    application.mount("/static", StaticFiles(directory="static"), name="static")

    # -------------------------------------------------------------------------
    # Route Registration
    # -------------------------------------------------------------------------
    application.include_router(health.router)
    application.include_router(web.router)
    application.include_router(discovery_router.router)
    application.include_router(discovery_views.router)

    return application


app = create_app()
