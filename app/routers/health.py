"""
Health & Readiness Probes for [STUDIO_NAME]
Conforms strictly to DOC-ARCH-018 and ADR-015.
"""

import time
from typing import Any
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health & Observability"])

# Record module initialization time for process uptime calculation
PROCESS_START_TIME = time.time()


@router.get("/live", summary="Liveness Probe")
async def health_live() -> dict[str, Any]:
    """
    Returns application process liveness and uptime.
    Used by container orchestration to verify ASGI process is alive.
    """
    uptime = round(time.time() - PROCESS_START_TIME, 2)
    return {
        "status": "alive",
        "uptime_seconds": uptime,
    }


@router.get("/ready", summary="Readiness Probe")
def health_ready(response: Response, db: Session = Depends(get_db)) -> dict:
    """
    Executes an empirical ping against Microsoft SQL Server 2022 Express.
    Returns 200 OK when connected with query latency, or 503 Service Unavailable on failure.
    """
    start = time.perf_counter()
    try:
        row = db.execute(text("SELECT 1")).fetchone()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        if row and row[0] == 1:
            return {
                "status": "ready",
                "database": {
                    "engine": "Microsoft SQL Server",
                    "status": "connected",
                    "latency_ms": latency_ms,
                },
            }
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "database": {
                "engine": "Microsoft SQL Server",
                "status": "unexpected_result",
            },
        }
    except Exception as exc:
        logger.error(f"Readiness probe failed database check: {exc.__class__.__name__}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "database": {
                "engine": "Microsoft SQL Server",
                "status": "disconnected",
                "error": "Database service unavailable",
            },
        }
