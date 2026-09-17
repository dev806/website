"""
Exception Architecture & Standard Error Envelopes for [STUDIO_NAME]
Conforms to DOC-ARCH-008 dual-interface error specification.
"""

from datetime import datetime, timezone
from typing import Any
from fastapi.responses import JSONResponse


def format_error_response(
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
    request_id: str = "",
    status_code: int = 400,
) -> JSONResponse:
    """Constructs the canonical JSON error envelope defined in DOC-ARCH-008."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            },
            "meta": {
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        },
    )


class AppException(Exception):
    """Base exception for all application-level errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: list[dict[str, Any]] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class EntityNotFoundError(AppException):
    """Raised when an entity is not found in persistent storage."""

    def __init__(self, entity_name: str, entity_id: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=404,
        )


class ValidationError(AppException):
    """Raised when business domain validation fails."""

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_FAILED",
            status_code=422,
            details=details,
        )


class UnauthorizedError(AppException):
    """Raised when authentication credentials or tokens are missing or invalid."""

    def __init__(self, message: str = "Authentication required or credentials invalid."):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenError(AppException):
    """Raised when an authenticated actor lacks permission to access an entity."""

    def __init__(self, message: str = "Access to this resource is prohibited."):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


class DatabaseError(AppException):
    """Raised on persistent storage connection or execution failures."""

    def __init__(self, message: str = "A database error occurred. Details suppressed for security."):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=503,
        )


class AIServiceError(AppException):
    """Raised when an AI Gateway operation fails."""

    def __init__(self, message: str = "The AI service encountered an error.", code: str = "AI_SERVICE_ERROR"):
        super().__init__(
            message=message,
            code=code,
            status_code=502,
        )
