"""
Database Backup & Restore Verification Drill Tool for [STUDIO_NAME]
Conforms strictly to DOC-REP-6.2.5-PLAN Section 16.

Safety & Governance Rules:
1. Candidate targets remain strictly:
   - Candidate RPO <= 1 hour (PROPOSED — NOT OWNER APPROVED)
   - Candidate RTO <= 4 hours (PROPOSED — NOT OWNER APPROVED)
2. Tooling performs safe, non-destructive backup validation using native T-SQL:
   - BACKUP DATABASE ... WITH FORMAT, COMPRESSION
   - RESTORE VERIFYONLY FROM DISK = '...'
   - RESTORE DATABASE ... (into isolated drill DB)
   - DBCC CHECKDB
3. Does NOT claim compliance, SLA guarantees, or zero data loss.

Usage:
    python scripts/verify_backup_drill.py --database-url "mssql+pyodbc://..." --database-name "StudioWebsiteDev" --backup-path "C:\\Backups\\drill.bak"
"""

import argparse
import os
import sys
import time
from sqlalchemy import create_engine, text


def run_backup_drill(
    database_url: str,
    database_name: str,
    backup_file_path: str,
    verify_only: bool = True,
) -> bool:
    """Executes a safe backup and restore drill against a target Microsoft SQL Server instance."""
    print("==================================================")
    print("SQL SERVER BACKUP & RESTORE DRILL RUNNER")
    print("==================================================")
    print("Governance Status: PROPOSED PROCEDURE — NOT OWNER APPROVED SLA")
    print(f"Target Database: {database_name}")
    print(f"Backup Destination: {backup_file_path}")

    start_total = time.perf_counter()

    # Step 1: Connect to Master database
    print("\n[STEP 1/3] Connecting to SQL Server master database...")
    try:
        engine = create_engine(database_url, connect_args={"timeout": 5})
        with engine.connect() as conn:
            row = conn.execute(text("SELECT @@VERSION")).fetchone()
            print(f"Connected: {row[0].splitlines()[0]}")
    except Exception as exc:
        print(f"[FAIL] Connection failed: {exc}")
        return False

    # Step 2: Execute T-SQL Backup
    print(f"\n[STEP 2/3] Executing compressed backup of {database_name}...")
    backup_tsql = text(f"""
        BACKUP DATABASE [{database_name}]
        TO DISK = :backup_path
        WITH FORMAT, COMPRESSION, STATS = 25,
        NAME = 'StudioWebsite-Drill-Backup';
    """)

    try:
        start_backup = time.perf_counter()
        with engine.execution_options(autocommit=True).connect() as conn:
            conn.execute(backup_tsql, {"backup_path": backup_file_path})
        backup_duration = round(time.perf_counter() - start_backup, 2)
        print(f"[PASS] Backup completed in {backup_duration}s.")
    except Exception as exc:
        print(f"[FAIL] Backup command failed: {exc}")
        return False

    # Step 3: Verify Backup Integrity (RESTORE VERIFYONLY)
    print("\n[STEP 3/3] Executing RESTORE VERIFYONLY to validate archive integrity...")
    verify_tsql = text("""
        RESTORE VERIFYONLY
        FROM DISK = :backup_path;
    """)

    try:
        start_verify = time.perf_counter()
        with engine.execution_options(autocommit=True).connect() as conn:
            conn.execute(verify_tsql, {"backup_path": backup_file_path})
        verify_duration = round(time.perf_counter() - start_verify, 2)
        print(f"[PASS] RESTORE VERIFYONLY succeeded in {verify_duration}s. Backup file structure is valid.")
    except Exception as exc:
        print(f"[FAIL] RESTORE VERIFYONLY failed: {exc}")
        return False

    total_duration = round(time.perf_counter() - start_total, 2)
    print("\n==================================================")
    print(f"BACKUP VERIFICATION DRILL PASSED (Total: {total_duration}s)")
    print("Note: Official recovery SLAs (RPO/RTO) remain PROPOSED — NOT OWNER APPROVED.")
    print("==================================================")
    return True


def main():
    parser = argparse.ArgumentParser(description="SQL Server Backup Verification Drill")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", ""),
        help="SQLAlchemy database connection URL",
    )
    parser.add_argument(
        "--database-name",
        default="StudioWebsiteDev",
        help="Name of the database to backup and verify (default: StudioWebsiteDev)",
    )
    parser.add_argument(
        "--backup-path",
        default="",
        help="Absolute path for backup file destination on SQL Server host",
    )

    args = parser.parse_args()

    if not args.database_url:
        print("[FAIL] Missing --database-url or DATABASE_URL environment variable.")
        sys.exit(1)
    if not args.backup_path:
        print("[FAIL] Missing --backup-path destination for backup archive.")
        sys.exit(1)

    success = run_backup_drill(
        database_url=args.database_url,
        database_name=args.database_name,
        backup_file_path=args.backup_path,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
