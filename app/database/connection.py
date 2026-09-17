"""
Database Engine & Connection Pool Management for [STUDIO_NAME]
Configures SQLAlchemy 2.x with pyodbc against Microsoft SQL Server 2022 Express.
"""

import time
from typing import Any, Optional
from sqlalchemy import Engine, create_engine, event
from app.config import Settings, get_settings
from app.shared.logging import correlation_id_ctx, get_logger
from app.shared.telemetry import emit_telemetry_event

logger = get_logger(__name__)

_engine: Optional[Engine] = None


def _setup_engine_events(engine: Engine, cfg: Settings) -> None:
    """Registers lightweight query performance listeners on the SQLAlchemy engine."""

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
    ) -> None:
        if context is not None:
            context._query_start_time = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
        conn: Any, cursor: Any, statement: str, parameters: Any, context: Any, executemany: bool
    ) -> None:
        if context is not None and hasattr(context, "_query_start_time"):
            duration_ms = round((time.perf_counter() - context._query_start_time) * 1000, 2)
            if duration_ms > cfg.slow_query_threshold_ms:
                # Extract first word as safe operation (e.g. SELECT, INSERT, UPDATE) — never parameters
                op = statement.strip().split()[0].upper() if statement else "QUERY"
                logger.warning(
                    f"Slow SQL query detected: {op} took {duration_ms}ms (threshold: {cfg.slow_query_threshold_ms}ms)",
                    extra={
                        "event": "slow_sql_query",
                        "duration_ms": duration_ms,
                        "operation": op,
                        "correlation_id": correlation_id_ctx.get(),
                    },
                )
                emit_telemetry_event(
                    "slow_sql_query",
                    {
                        "operation": op,
                        "duration_ms": duration_ms,
                    },
                    is_operational=True,
                    level=10,  # DEBUG level for internal event to avoid duplicate warnings
                )


def create_db_engine(settings: Optional[Settings] = None) -> Engine:
    """Creates and configures a SQLAlchemy engine with connection pooling for SQL Server."""
    cfg = settings or get_settings()
    db_url = cfg.get_database_url_str()

    logger.info("Initializing SQL Server engine with pyodbc threadpool strategy")
    engine = create_engine(
        db_url,
        pool_size=cfg.database_pool_size,
        max_overflow=cfg.database_max_overflow,
        pool_recycle=cfg.database_pool_recycle,
        pool_pre_ping=True,
        echo=cfg.debug,
    )
    _setup_engine_events(engine, cfg)
    return engine


def get_engine(settings: Optional[Settings] = None) -> Engine:
    """Returns the process-wide SQLAlchemy engine singleton."""
    global _engine
    if _engine is None:
        _engine = create_db_engine(settings)
    return _engine


def dispose_engine() -> None:
    """Disposes the process-wide engine connection pool during application shutdown."""
    global _engine
    if _engine is not None:
        logger.info("Disposing SQL Server connection pool")
        _engine.dispose()
        _engine = None
