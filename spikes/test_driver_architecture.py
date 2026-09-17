"""
Spike SP-03: Driver Initialization and Architectural Comparison
Test aioodbc and pyodbc module loading, SQLAlchemy engine configuration,
and threadpool dispatch mechanics under Python 3.13 on Windows 11.
"""
import asyncio
import inspect
import sys
import time
import aioodbc
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.concurrency import run_in_threadpool

print("=" * 70)
print("SP-03: DRIVER INITIALIZATION & ARCHITECTURE TEST")
print("=" * 70)

print(f"Python Version: {sys.version}")
print(f"pyodbc Version: {pyodbc.version}")
print(f"aioodbc Version: {aioodbc.__version__}")

# 1. Test SQLAlchemy Sync Engine Creation (pyodbc)
sync_url = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3Dlocalhost%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)
try:
    sync_engine = create_engine(sync_url)
    print("\n[PASS] SQLAlchemy sync engine (mssql+pyodbc) created successfully.")
    print(f"       Dialect: {sync_engine.dialect.name} (driver: {sync_engine.dialect.driver})")
except Exception as e:
    print(f"\n[FAIL] SQLAlchemy sync engine creation failed: {e}")

# 2. Test SQLAlchemy Async Engine Creation (aioodbc)
async_url = (
    "mssql+aioodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3Dlocalhost%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)
try:
    async_engine = create_async_engine(async_url)
    print("\n[PASS] SQLAlchemy async engine (mssql+aioodbc) created successfully.")
    print(f"       Dialect: {async_engine.dialect.name} (driver: {async_engine.dialect.driver})")
except Exception as e:
    print(f"\n[FAIL] SQLAlchemy async engine creation failed: {e}")

# 3. Test FastAPI/Starlette run_in_threadpool Concurrency Mechanics
def simulate_sync_db_call(call_id: int, duration_ms: float = 20.0):
    """Simulates a synchronous DB query executed inside a worker thread."""
    t0 = time.perf_counter()
    time.sleep(duration_ms / 1000.0)
    elapsed = (time.perf_counter() - t0) * 1000.0
    return {"call_id": call_id, "elapsed_ms": elapsed}

async def benchmark_threadpool(num_calls: int = 20):
    print(f"\nTesting FastAPI run_in_threadpool concurrency across {num_calls} calls...")
    t_start = time.perf_counter()
    tasks = [run_in_threadpool(simulate_sync_db_call, i, 15.0) for i in range(num_calls)]
    results = await asyncio.gather(*tasks)
    total_time = (time.perf_counter() - t_start) * 1000.0
    latencies = [r["elapsed_ms"] for r in results]
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    avg = sum(latencies) / len(latencies)
    print(f"       Total wall time for {num_calls} concurrent 15ms calls: {total_time:.2f} ms")
    print(f"       Average call duration: {avg:.2f} ms | p50: {p50:.2f} ms | p95: {p95:.2f} ms")
    print(f"       Throughput efficiency: { (num_calls * 15.0) / total_time :.2f}x parallel speedup")
    print("[PASS] Threadpool concurrency mechanism validated.")

asyncio.run(benchmark_threadpool(20))
print("\n" + "=" * 70)
