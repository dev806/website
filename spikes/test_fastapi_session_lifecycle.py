"""
Spike SP-05: FastAPI Database Session Lifecycle Spike
Validates application lifespan, dependency session lifecycle, transaction handling,
clean session release, and real database readiness probe (/health/ready).
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError, InterfaceError
from starlette.concurrency import run_in_threadpool
import pytest
from httpx import AsyncClient, ASGITransport

print("=" * 70)
print("SP-05: FASTAPI DATABASE SESSION LIFECYCLE SPIKE")
print("=" * 70)

# Mock/Configured DB session factory for spike
class SpikeSessionManager:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.opened = 0
        self.closed = 0
        self.rolled_back = 0
        self.committed = 0

    def get_session(self):
        return SpikeSession(self)

class SpikeSession:
    def __init__(self, manager: SpikeSessionManager):
        self.manager = manager
        self.manager.opened += 1
        self.is_active = True

    def execute_ping(self):
        if self.manager.should_fail:
            raise OperationalError("SQL Server service unreachable", params=None, orig=Exception("Connection refused"))
        return 1

    def commit(self):
        self.manager.committed += 1

    def rollback(self):
        self.manager.rolled_back += 1

    def close(self):
        self.is_active = False
        self.manager.closed += 1

# Instantiate test manager
db_manager = SpikeSessionManager(should_fail=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup verification
    print("[Lifespan] Application starting up. Initializing resources...")
    yield
    # Shutdown verification
    print("[Lifespan] Application shutting down. Releasing pools...")

app = FastAPI(title="Spike-Session-Lifecycle", lifespan=lifespan)

# Dependency pattern
async def get_db_session():
    session = db_manager.get_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/health/live")
async def liveness():
    return {"status": "live"}

@app.get("/health/ready")
async def readiness(session: SpikeSession = Depends(get_db_session)):
    try:
        # Run DB ping in threadpool
        ping_result = await run_in_threadpool(session.execute_ping)
        return {"status": "ready", "database": "connected", "ping": ping_result}
    except (OperationalError, InterfaceError) as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unreachable", "detail": str(e)}
        )

# Test runner using httpx ASGITransport
@pytest.mark.asyncio
async def test_session_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test liveness
        r_live = await client.get("/health/live")
        assert r_live.status_code == 200
        assert r_live.json() == {"status": "live"}
        print("[PASS] GET /health/live returned 200 OK")

        # 2. Test readiness when DB is operational
        db_manager.should_fail = False
        r_ready = await client.get("/health/ready")
        assert r_ready.status_code == 200
        assert r_ready.json()["database"] == "connected"
        assert db_manager.opened == 1
        assert db_manager.closed == 1
        print("[PASS] GET /health/ready returned 200 OK when DB is ready. Session opened & closed cleanly.")

        # 3. Test readiness when DB is unreachable
        db_manager.should_fail = True
        r_unready = await client.get("/health/ready")
        assert r_unready.status_code == 503
        assert r_unready.json()["status"] == "degraded"
        assert db_manager.opened == 2
        assert db_manager.closed == 2
        print("[PASS] GET /health/ready returned 503 Service Unavailable when DB is unreachable.")

        # 4. Test exception rollback in session dependency
        @app.get("/test-error")
        async def trigger_error(session: SpikeSession = Depends(get_db_session)):
            raise RuntimeError("Simulated transaction failure")

        try:
            await client.get("/test-error")
        except RuntimeError:
            pass
        assert db_manager.rolled_back == 1
        assert db_manager.closed == 3
        print("[PASS] Session rollback triggered upon unhandled exception; session closed cleanly.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_session_lifecycle())
    print("\n[PASS] All FastAPI Database Session Lifecycle tests passed successfully.")
    print("=" * 70)
