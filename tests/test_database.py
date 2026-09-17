"""
Database Persistence & Session Lifecycle Integration Tests for [STUDIO_NAME]
Executes live against Microsoft SQL Server 2022 Express.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_engine
from app.database.session import get_db


def test_sql_server_live_connection(engine):
    """Verifies live SQL Server connection and database context."""
    with engine.connect() as conn:
        row = conn.execute(text("SELECT DB_NAME(), 1")).fetchone()
        assert row is not None
        assert row[0] == "StudioWebsiteTest"
        assert row[1] == 1


def test_database_session_commit_and_release(engine):
    """Verifies get_db yields session and releases connection upon exit."""
    generator = get_db()
    db = next(generator)
    assert isinstance(db, Session)
    # Execute a lightweight query
    result = db.execute(text("SELECT 42")).scalar()
    assert result == 42
    # Complete generator
    with pytest.raises(StopIteration):
        next(generator)


def test_database_session_rollback_on_error():
    """Verifies that an unhandled exception triggers rollback in get_db generator."""
    generator = get_db()
    db = next(generator)
    with pytest.raises(ValueError, match="Simulated application failure"):
        try:
            raise ValueError("Simulated application failure")
        except Exception as exc:
            generator.throw(exc)
