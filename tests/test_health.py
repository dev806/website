"""
Health & Observability Probe Tests for [STUDIO_NAME]
"""

import pytest
from app.database.session import get_db
from app.main import app


@pytest.mark.asyncio
async def test_health_live_probe(async_client):
    """Verifies that /health/live returns process health and uptime."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "uptime_seconds" in data
    assert "X-Correlation-ID" in response.headers


@pytest.mark.asyncio
async def test_health_ready_probe(async_client):
    """Verifies that /health/ready executes an active SQL Server query."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"]["status"] == "connected"
    assert data["database"]["engine"] == "Microsoft SQL Server"
    assert "latency_ms" in data["database"]


@pytest.mark.asyncio
async def test_health_ready_probe_database_failure(async_client):
    """Verifies that /health/ready returns 503 when the database execution fails."""

    class FailingSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Simulated SQL Server connection failure")

    def mock_failing_db():
        yield FailingSession()

    app.dependency_overrides[get_db] = mock_failing_db
    try:
        response = await async_client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"]["status"] == "disconnected"
    finally:
        app.dependency_overrides.clear()
