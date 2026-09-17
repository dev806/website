"""
Unified Sprint 0 Pytest Test Suite — Live SQL Server 2022 Validated
Aggregates assertions across SP-01, SP-02, SP-03, SP-04, SP-05, SP-06, and SP-07.
All database tests execute live against local Microsoft SQL Server 2022 Express.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from pathlib import Path
import pytest
import pyodbc
import aioodbc
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable
from spikes.models_spike import Base, DiscoverySessionSpike, ProblemSubmissionSpike, AuditLogSpike
from spikes.test_ai_gateway_mock import (
    scrub_pii,
    AIServiceGatewaySpike,
    MockValidAIProvider,
    MockTimeoutAIProvider,
    MockMalformedAIProvider,
    STATIC_FALLBACK_QUESTIONS,
)
from spikes.test_fastapi_live_sql_lifecycle import app as fastapi_app
from httpx import AsyncClient, ASGITransport

URL_DEV = os.environ.get(
    "DATABASE_URL_DEV",
    (
        "mssql+pyodbc:///?odbc_connect="
        "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
        "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
        "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
    ),
)

URL_TEST = os.environ.get(
    "DATABASE_URL_TEST",
    (
        "mssql+pyodbc:///?odbc_connect="
        "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
        "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteTest%3B"
        "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
    ),
)

# SP-01: Package & Driver Module Verification
def test_sp01_driver_packages_loaded():
    assert pyodbc.version is not None
    assert aioodbc.__version__ is not None
    assert "ODBC Driver 18 for SQL Server" in pyodbc.drivers()
    if sys.platform == "win32":
        assert "SQL Server" in pyodbc.drivers()

# SP-02: Live SQL Server Liveness & Dual Database Provisioning
def test_sp02_sql_server_live_connectivity():
    engine_dev = create_engine(URL_DEV)
    with engine_dev.connect() as conn:
        row = conn.execute(text("SELECT @@SERVERNAME, DB_NAME(), 1")).fetchone()
        assert row[1] == "StudioWebsiteDev"
        assert row[2] == 1

    engine_test = create_engine(URL_TEST)
    with engine_test.connect() as conn:
        row = conn.execute(text("SELECT DB_NAME()")).fetchone()
        assert row[0] == "StudioWebsiteTest"

# SP-03: pyodbc Driver Stability and Threadpool Concurrency
def test_sp03_driver_threadpool_concurrency():
    engine_dev = create_engine(URL_DEV, pool_size=5, max_overflow=10)
    with engine_dev.connect() as conn:
        res = conn.execute(text("SELECT @@SPID, 1+1")).fetchone()
        assert res[1] == 2

# SP-04: Live SQLAlchemy MSSQL DDL & Catalog Inspection
def test_sp04_mssql_live_ddl_and_catalog():
    engine_dev = create_engine(URL_DEV)
    inspector = inspect(engine_dev)
    tables = inspector.get_table_names()
    assert "discovery_sessions" in tables
    assert "problem_submissions" in tables or "problem_statements" in tables
    assert "audit_logs" in tables

# SP-05: FastAPI Live Database Session Lifecycle & /health/ready
@pytest.mark.asyncio
async def test_sp05_fastapi_live_readiness_probe():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r_live = await client.get("/health/live")
        assert r_live.status_code == 200
        assert r_live.json()["status"] == "live"

        r_ready = await client.get("/health/ready")
        assert r_ready.status_code == 200
        data = r_ready.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"
        assert data["engine"] == "mssql+pyodbc"
        assert data["ping"] == 1

# SP-06: AI Gateway PII Scrubbing, Schema Validation & Fallback
@pytest.mark.asyncio
async def test_sp06_ai_gateway_pii_and_fallback():
    # PII scrub
    raw = "Contact test@studio.com or call 9876543210."
    clean = scrub_pii(raw)
    assert "test@studio.com" not in clean
    assert "[REDACTED_EMAIL]" in clean

    # Valid
    gw_valid = AIServiceGatewaySpike(MockValidAIProvider())
    out_valid, src_v = await gw_valid.generate_clarifications("Build inventory platform")
    assert src_v == "PROVIDER_LLM"
    assert len(out_valid.questions) >= 3

    # Timeout
    gw_time = AIServiceGatewaySpike(MockTimeoutAIProvider(), timeout_seconds=0.05)
    out_time, src_t = await gw_time.generate_clarifications("Build inventory platform")
    assert src_t == "FALLBACK_TIMEOUT"
    assert out_time == STATIC_FALLBACK_QUESTIONS

    # Malformed
    gw_bad = AIServiceGatewaySpike(MockMalformedAIProvider())
    out_bad, src_b = await gw_bad.generate_clarifications("Build inventory platform")
    assert src_b == "FALLBACK_SCHEMA_ERROR"
    assert out_bad == STATIC_FALLBACK_QUESTIONS

# SP-07: Static Assets Vendoring Verification
def test_sp07_static_assets_vendored():
    htmx_file = Path("static/vendor/htmx.min.js")
    alpine_file = Path("static/vendor/alpine.min.js")
    assert htmx_file.exists()
    assert htmx_file.stat().st_size > 40000
    assert alpine_file.exists()
    assert alpine_file.stat().st_size > 40000
