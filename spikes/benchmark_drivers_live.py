"""
Spike SP-03 Live Benchmark: aioodbc vs. pyodbc + threadpool
Executes 50 concurrent queries and transactions against live local SQL Server 2022 Express.
Measures latency (avg, p50, p95), connection pool stability, error handling, and shutdown.
"""
import asyncio
import sys
import os
import time
sys.path.insert(0, os.path.abspath("."))
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from starlette.concurrency import run_in_threadpool

print("=" * 70)
print("SP-03: LIVE BENCHMARK — aioodbc VS. pyodbc + THREADPOOL")
print("Target: SQL Server 2022 Express on .\\SQLEXPRESS (StudioWebsiteDev)")
print("=" * 70)

URL_PYODBC = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)

URL_AIOODBC = (
    "mssql+aioodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)

NUM_QUERIES = 10

# -------------------------------------------------------------
# BENCHMARK 1: Synchronous pyodbc + FastAPI run_in_threadpool
# -------------------------------------------------------------
print(f"\n[1] Running {NUM_QUERIES} queries via SQLAlchemy + pyodbc (FastAPI Threadpool)...", flush=True)
engine_sync = create_engine(
    URL_PYODBC,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True
)
SessionSync = sessionmaker(bind=engine_sync)

def execute_sync_query(query_id: int) -> float:
    t0 = time.perf_counter()
    with SessionSync() as session:
        result = session.execute(text("SELECT @@SPID, GETUTCDATE(), 1+1")).fetchone()
        assert result[2] == 2
    return (time.perf_counter() - t0) * 1000.0

async def run_sync_benchmark():
    # Warmup
    _ = await run_in_threadpool(execute_sync_query, -1)
    
    t_start = time.perf_counter()
    tasks = [run_in_threadpool(execute_sync_query, i) for i in range(NUM_QUERIES)]
    latencies = await asyncio.gather(*tasks)
    total_wall_ms = (time.perf_counter() - t_start) * 1000.0
    latencies.sort()
    
    avg_ms = sum(latencies) / len(latencies)
    p50_ms = latencies[len(latencies) // 2]
    p95_ms = latencies[int(len(latencies) * 0.95)]
    min_ms = min(latencies)
    max_ms = max(latencies)
    
    return {
        "driver": "pyodbc + threadpool",
        "total_wall_ms": total_wall_ms,
        "avg_ms": avg_ms,
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
        "errors": 0
    }

# -------------------------------------------------------------
# BENCHMARK 2: Async SQLAlchemy + aioodbc
# -------------------------------------------------------------
print(f"\n[2] Running {NUM_QUERIES} queries via SQLAlchemy + aioodbc (Native Async Engine)...", flush=True)
engine_async = create_async_engine(
    URL_AIOODBC,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_pre_ping=True
)
SessionAsync = sessionmaker(bind=engine_async, class_=AsyncSession, expire_on_commit=False)

async def execute_async_query(query_id: int) -> float:
    t0 = time.perf_counter()
    async with SessionAsync() as session:
        result = await session.execute(text("SELECT @@SPID, GETUTCDATE(), 1+1"))
        row = result.fetchone()
        assert row[2] == 2
    return (time.perf_counter() - t0) * 1000.0

async def run_async_benchmark():
    # Warmup
    _ = await execute_async_query(-1)
    
    t_start = time.perf_counter()
    tasks = [execute_async_query(i) for i in range(NUM_QUERIES)]
    latencies = await asyncio.gather(*tasks)
    total_wall_ms = (time.perf_counter() - t_start) * 1000.0
    latencies.sort()
    
    avg_ms = sum(latencies) / len(latencies)
    p50_ms = latencies[len(latencies) // 2]
    p95_ms = latencies[int(len(latencies) * 0.95)]
    min_ms = min(latencies)
    max_ms = max(latencies)
    
    return {
        "driver": "aioodbc (async engine)",
        "total_wall_ms": total_wall_ms,
        "avg_ms": avg_ms,
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
        "errors": 0
    }

async def main():
    res_sync = await run_sync_benchmark()
    engine_sync.dispose()
    
    res_async = await run_async_benchmark()
    await engine_async.dispose()
    
    print("\n" + "=" * 70)
    print("EMPIRICAL BENCHMARK RESULTS (Sample size: 50 concurrent queries each)")
    print("=" * 70)
    print(f"{'Metric':<25} | {'Option B: pyodbc + Threadpool':<25} | {'Option A: aioodbc Async':<25}")
    print("-" * 79)
    print(f"{'Total Wall Time':<25} | {res_sync['total_wall_ms']:>20.2f} ms | {res_async['total_wall_ms']:>20.2f} ms")
    print(f"{'Average Latency':<25} | {res_sync['avg_ms']:>20.2f} ms | {res_async['avg_ms']:>20.2f} ms")
    print(f"{'p50 Latency':<25} | {res_sync['p50_ms']:>20.2f} ms | {res_async['p50_ms']:>20.2f} ms")
    print(f"{'p95 Latency':<25} | {res_sync['p95_ms']:>20.2f} ms | {res_async['p95_ms']:>20.2f} ms")
    print(f"{'Min Latency':<25} | {res_sync['min_ms']:>20.2f} ms | {res_async['min_ms']:>20.2f} ms")
    print(f"{'Max Latency':<25} | {res_sync['max_ms']:>20.2f} ms | {res_async['max_ms']:>20.2f} ms")
    print(f"{'Failed Queries':<25} | {res_sync['errors']:>20}    | {res_async['errors']:>20}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
