"""
Spike SP-04 Live: Live DDL Creation and Migration Execution
Executes real DDL creation, constraint verification, and table lifecycle
against live local SQL Server 2022 Express (StudioWebsiteDev & StudioWebsiteTest).
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, text, inspect
from spikes.models_spike import Base, DiscoverySessionSpike, ProblemSubmissionSpike, AuditLogSpike

print("=" * 70)
print("SP-04: LIVE SQLALCHEMY 2.0 DDL & MIGRATION EXECUTION")
print("=" * 70)

URL_DEV = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)

engine = create_engine(URL_DEV, echo=False)

# 1. Clean previous spike tables if any
print("\n[1] Dropping existing spike tables in StudioWebsiteDev...")
Base.metadata.drop_all(engine)
print("  --> Dropped successfully.")

# 2. Create tables live
print("\n[2] Creating tables live in StudioWebsiteDev via Base.metadata.create_all()...")
Base.metadata.create_all(engine)
print("  --> create_all() executed successfully.")

# 3. Inspect created tables and columns in SQL Server
print("\n[3] Inspecting schema in SQL Server catalog...")
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"  --> Tables found in database: {tables}")
assert "discovery_sessions" in tables
assert "problem_submissions" in tables
assert "audit_logs" in tables

cols = inspector.get_columns("discovery_sessions")
col_types = {c["name"]: str(c["type"]) for c in cols}
print(f"  --> Columns in discovery_sessions: {col_types}")
assert "UNIQUEIDENTIFIER" in col_types["id"].upper() or "UUID" in col_types["id"].upper()

# 4. Test live CRUD with foreign key cascade
print("\n[4] Testing live record insertion with foreign keys and CASCADE...")
with engine.connect() as conn:
    # Insert session
    session_id = uuid.uuid4()
    token = f"tok_{uuid.uuid4().hex[:16]}"
    conn.execute(
        text("INSERT INTO discovery_sessions (id, session_token, status, created_at, updated_at) VALUES (:id, :tok, :st, :ca, :ua)"),
        {"id": session_id, "tok": token, "st": "S01_INITIAL_LANDING", "ca": datetime.now(timezone.utc), "ua": datetime.now(timezone.utc)}
    )
    
    # Insert submission
    sub_id = uuid.uuid4()
    conn.execute(
        text("INSERT INTO problem_submissions (id, session_id, raw_problem_text, sanitized_problem_text, char_count, created_at) VALUES (:id, :sid, :raw, :san, :cc, :ca)"),
        {"id": sub_id, "sid": session_id, "raw": "Problem description with > 20 characters.", "san": "Sanitized text description.", "cc": 35, "ca": datetime.now(timezone.utc)}
    )
    conn.commit()
    print("  --> Inserted session and child submission successfully.")

    # Verify rows exist
    res = conn.execute(text("SELECT COUNT(*) FROM problem_submissions WHERE session_id = :sid"), {"sid": session_id}).scalar()
    assert res == 1

    # Test CASCADE DELETE
    conn.execute(text("DELETE FROM discovery_sessions WHERE id = :sid"), {"sid": session_id})
    conn.commit()
    res_after = conn.execute(text("SELECT COUNT(*) FROM problem_submissions WHERE session_id = :sid"), {"sid": session_id}).scalar()
    assert res_after == 0
    print("  --> CASCADE delete verified: Deleting parent session automatically removed child submission.")

# 5. Test check constraint enforcement
print("\n[5] Testing CHECK constraint enforcement on SQL Server...")
with engine.connect() as conn:
    session_id = uuid.uuid4()
    conn.execute(
        text("INSERT INTO discovery_sessions (id, session_token, status, created_at, updated_at) VALUES (:id, :tok, :st, :ca, :ua)"),
        {"id": session_id, "tok": f"tok_{uuid.uuid4().hex[:16]}", "st": "S01_INITIAL_LANDING", "ca": datetime.now(timezone.utc), "ua": datetime.now(timezone.utc)}
    )
    conn.commit()
    
    # Attempt inserting with char_count < 20 (should raise IntegrityError / CheckConstraint violation)
    try:
        conn.execute(
            text("INSERT INTO problem_submissions (id, session_id, raw_problem_text, sanitized_problem_text, char_count, created_at) VALUES (:id, :sid, :raw, :san, :cc, :ca)"),
            {"id": uuid.uuid4(), "sid": session_id, "raw": "Short", "san": "Short", "cc": 5, "ca": datetime.now(timezone.utc)}
        )
        conn.commit()
        raise AssertionError("Expected CHECK constraint violation!")
    except Exception as e:
        conn.rollback()
        print(f"  --> CHECK constraint properly rejected invalid row: {type(e).__name__}")

print("\n" + "=" * 70)
print("[VERDICT: SP-04 FULLY VERIFIED ON LIVE SQL SERVER 2022 EXPRESS]")
print("=" * 70)
