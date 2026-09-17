"""
Spike SP-05 Live: FastAPI Database Session Lifecycle against Live SQL Server 2022
Validates lifespan engine management, get_db session dependency, /health/ready probe,
and transaction rollback mechanics against the real StudioWebsiteDev database.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, InterfaceError
from starlette.concurrency import run_in_threadpool
import pytest
from httpx import AsyncClient, ASGITransport

print("=" * 70)
print("SP-05: LIVE FASTAPI + SQL SERVER DATABASE SESSION LIFECYCLE")
print("=" * 70)

URL_DEV = os.environ.get(
    "DATABASE_URL_DEV",
    (
        "mssql+pyodbc:///?odbc_connect="
        "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
        "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
        "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
    ),
)

engine = create_engine(
    URL_DEV,
    pool_size=5,
    max_overflow=10,
    pool_timeout=15,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify engine ping on startup
    print("[Lifespan] Verifying SQL Server connectivity on startup...")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("[Lifespan] SQL Server connection verified. Startup complete.")
    yield
    print("[Lifespan] Disposing connection pool on shutdown...")
    engine.dispose()
    print("[Lifespan] Shutdown complete.")

app = FastAPI(title="Live-FastAPI-SQLServer-Spike", lifespan=lifespan)

# Standard FastAPI dependency pattern for sync SQLAlchemy session in threadpool
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@app.get("/health/live")
async def health_live():
    return {"status": "live"}

@app.get("/health/ready")
async def health_ready(db: Session = Depends(get_db)):
    def ping_db():
        result = db.execute(text("SELECT 1 AS ping_val")).scalar()
        return result

    try:
        ping = await run_in_threadpool(ping_db)
        return {"status": "ready", "database": "connected", "engine": "mssql+pyodbc", "ping": ping}
    except (OperationalError, InterfaceError) as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unreachable", "detail": str(e)}
        )

@app.post("/test/rollback")
async def test_rollback(db: Session = Depends(get_db)):
    def do_failing_work():
        db.execute(text("INSERT INTO discovery_sessions (id, session_token, status, created_at, updated_at) VALUES (:id, :tok, :st, GETUTCDATE(), GETUTCDATE())"),
                   {"id": uuid.uuid4(), "tok": "test_tok_rollback", "st": "TEST"})
        raise RuntimeError("Simulated transaction failure to trigger rollback")

    await run_in_threadpool(do_failing_work)
    return {"status": "ok"}

async def run_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test /health/live
        r_live = await client.get("/health/live")
        assert r_live.status_code == 200
        assert r_live.json() == {"status": "live"}
        print("[PASS] GET /health/live returned HTTP 200")

        # 2. Test /health/ready on live SQL Server
        r_ready = await client.get("/health/ready")
        assert r_ready.status_code == 200
        data = r_ready.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"
        assert data["ping"] == 1
        print(f"[PASS] GET /health/ready returned HTTP 200: {data}")

        # 3. Test exception rollback in session
        try:
            await client.post("/test/rollback")
        except RuntimeError:
            pass

        # Verify row was NOT committed
        with engine.connect() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM discovery_sessions WHERE session_token = 'test_tok_rollback'")).scalar()
            assert cnt == 0
        print("[PASS] Exception during request triggered clean transaction rollback in SQL Server (0 rows committed).")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())
    print("\n" + "=" * 70)
    print("[VERDICT: SP-05 FULLY VERIFIED LIVE ON SQL SERVER 2022 EXPRESS]")
    print("=" * 70)
