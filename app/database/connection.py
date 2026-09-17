"""
Database Engine & Connection Pool Management for [STUDIO_NAME]
Configures SQLAlchemy 2.x with pyodbc against Microsoft SQL Server 2022 Express.
"""

from typing import Optional
from sqlalchemy import Engine, create_engine
from app.config import Settings, get_settings
from app.shared.logging import get_logger

logger = get_logger(__name__)

_engine: Optional[Engine] = None


def create_db_engine(settings: Optional[Settings] = None) -> Engine:
    """Creates and configures a SQLAlchemy engine with connection pooling for SQL Server."""
    cfg = settings or get_settings()
    db_url = cfg.get_database_url_str()

    logger.info("Initializing SQL Server engine with pyodbc threadpool strategy")
    return create_engine(
        db_url,
        pool_size=cfg.database_pool_size,
        max_overflow=cfg.database_max_overflow,
        pool_recycle=cfg.database_pool_recycle,
        pool_pre_ping=True,
        echo=cfg.debug,
    )


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
