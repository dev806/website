"""
Database Session Lifecycle & FastAPI Dependency for [STUDIO_NAME]
Executes synchronous pyodbc operations across Starlette worker threadpools.
"""

from collections.abc import Generator
from sqlalchemy.orm import Session, sessionmaker
from app.database.connection import get_engine
from app.shared.logging import get_logger

logger = get_logger(__name__)


def get_session_factory(bind_engine=None) -> sessionmaker[Session]:
    """Constructs a sessionmaker bound to the active engine."""
    engine = bind_engine or get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session.
    Automatically commits on clean completion, rolls back on exceptions,
    and guarantees connection release back to the pool in a finally block.
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning(f"Database session rolled back due to error: {exc.__class__.__name__}")
        raise
    finally:
        db.close()
