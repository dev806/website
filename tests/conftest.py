"""
Pytest Test Fixtures & Configuration for [STUDIO_NAME]
All database tests execute live against local Microsoft SQL Server 2022 Express (StudioWebsiteTest).
"""

import os
import sys
from collections.abc import AsyncGenerator, Generator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

# Ensure test environment mode is active
os.environ["APP_ENV"] = "testing"

from app.config import get_settings
from app.database.connection import create_db_engine, get_engine
from app.database.session import get_db
from app.main import app, _rate_limit_store


@pytest.fixture(autouse=True)
def clear_rate_limits():
    """Resets in-memory rate limit counters before each test to prevent cross-test 429s."""
    _rate_limit_store.clear()
    yield
    _rate_limit_store.clear()

settings = get_settings()


@pytest.fixture(scope="session")
def engine() -> Engine:
    """Session-scoped SQLAlchemy engine bound to StudioWebsiteTest."""
    eng = create_db_engine(settings)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    """Function-scoped transactional session for database tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = session_factory()

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP test client for FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
