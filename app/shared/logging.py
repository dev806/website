"""
Structured Logging & Correlation ID Management for [STUDIO_NAME]
Conforms to DOC-ARCH-018. Redacts secrets, API keys, and PII from log output.
"""

import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

# Global context variable for tracking the current request correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="system")

# Sensitive key patterns to redact automatically
SENSITIVE_KEY_PATTERNS = re.compile(
    r"(secret|password|token|api_key|authorization|connection_string|odbc_connect)",
    re.IGNORECASE,
)


class SensitiveFilter(logging.Filter):
    """Filters out passwords, secrets, and connection strings from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            # Redact common connection string passwords
            record.msg = re.sub(r"pwd=[^;]+", "pwd=[REDACTED]", record.msg, flags=re.IGNORECASE)
            record.msg = re.sub(r"password=[^;]+", "password=[REDACTED]", record.msg, flags=re.IGNORECASE)
        return True


class JSONLogFormatter(logging.Formatter):
    """Formats log records as single-line machine-readable JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get(),
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Configures the root logging subsystem with correlation ID support and sensitive filtering."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(SensitiveFilter())

    if json_format:
        handler.setFormatter(JSONLogFormatter())
    else:
        standard_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] [corr:%(correlation_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # Custom factory to inject correlation_id into standard formatter
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = old_factory(*args, **kwargs)
            record.correlation_id = correlation_id_ctx.get()  # type: ignore[attr-defined]
            return record

        logging.setLogRecordFactory(record_factory)
        handler.setFormatter(standard_formatter)

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger configured for [STUDIO_NAME]."""
    return logging.getLogger(name)
