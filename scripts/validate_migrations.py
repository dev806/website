"""
Safe Migration Validation Tooling for [STUDIO_NAME]
Conforms strictly to DOC-REP-6.2.5-PLAN Section 8.

Safety Rules:
1. Targets an explicitly supplied database URL or target environment (staging / dev / test).
2. NEVER defaults to production.
3. Requires explicit confirmation (--force-production-confirmation) if production is detected in target.
4. Fails safely if target configuration is missing.
5. Verifies Alembic head revision after execution.
6. Provides clear failure output with diagnostic logs.

Usage:
    python scripts/validate_migrations.py --target-env staging --database-url "mssql+pyodbc://..."
    python scripts/validate_migrations.py --target-env test --database-url "mssql+pyodbc://..."
"""

import argparse
import os
import subprocess
import sys
from sqlalchemy import create_engine, text

# Known expected Alembic head revision in current repository
EXPECTED_ALEMBIC_HEAD = "4941998763bd"


def validate_migrations(
    database_url: str,
    target_env: str,
    force_production: bool = False,
    dry_run: bool = False,
) -> bool:
    """Safely executes and validates Alembic migrations against an explicitly targeted database."""
    print("==================================================")
    print("ALEMBIC MIGRATION VALIDATION RUNNER")
    print("==================================================")
    print(f"Target Environment: {target_env}")
    
    # Mask password for display
    display_url = database_url
    if ":" in database_url and "@" in database_url:
        parts = database_url.split("@")
        cred_part = parts[0]
        if ":" in cred_part:
            scheme_user = cred_part.rsplit(":", 1)[0]
            display_url = f"{scheme_user}:***@{parts[1]}"
    print(f"Target Database URL: {display_url}")

    # Safety Guard: Production Environment Protection
    is_prod_target = (
        target_env.lower() in ("production", "prod")
        or "production" in database_url.lower()
        or "prod" in database_url.lower()
    )

    if is_prod_target and not force_production:
        print("\n[CRITICAL SAFETY STOP]")
        print("Target appears to be a PRODUCTION database.")
        print("Automatic execution is blocked to prevent unintended production schema modifications.")
        print("To proceed, you must supply: --force-production-confirmation")
        return False

    # Check 1: Live Database Connectivity Check
    print("\n[STEP 1/4] Verifying database connectivity and engine compatibility...")
    try:
        engine = create_engine(database_url, connect_args={"timeout": 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION, DB_NAME()")).fetchone()
            if result:
                version_info = result[0].splitlines()[0]
                db_name = result[1]
                print(f"Connected successfully to DB: {db_name}")
                print(f"SQL Server Version: {version_info}")
            else:
                print("Connected, but could not determine SQL Server version.")
    except Exception as exc:
        print(f"[FAIL] Database connectivity check failed: {exc}")
        return False

    # Check 2: Inspect Current Revision
    print("\n[STEP 2/4] Inspecting current Alembic revision...")
    env_copy = os.environ.copy()
    env_copy["DATABASE_URL"] = database_url

    try:
        curr_cmd = [sys.executable, "-m", "alembic", "current"]
        curr_proc = subprocess.run(curr_cmd, env=env_copy, capture_output=True, text=True)
        print(f"Current migration state:\n{curr_proc.stdout.strip() or '(no revision table found)'}")
    except Exception as exc:
        print(f"[WARN] Unable to read current revision: {exc}")

    # Check 3: Apply Migrations (or Dry-Run)
    if dry_run:
        print("\n[STEP 3/4] Dry-run requested: skipping 'alembic upgrade head'.")
    else:
        print("\n[STEP 3/4] Executing 'alembic upgrade head'...")
        try:
            up_cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
            up_proc = subprocess.run(up_cmd, env=env_copy, capture_output=True, text=True)
            if up_proc.returncode != 0:
                print(f"[FAIL] Alembic upgrade command failed (exit code {up_proc.returncode}):")
                print(up_proc.stderr)
                return False
            print("Upgrade command executed successfully.")
            if up_proc.stdout.strip():
                print(up_proc.stdout.strip())
        except Exception as exc:
            print(f"[FAIL] Error invoking alembic: {exc}")
            return False

    # Check 4: Verify Alembic Head Revision in Database
    print("\n[STEP 4/4] Verifying alembic_version table against expected HEAD...")
    try:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT version_num FROM dbo.alembic_version")).fetchone()
            if not row:
                print("[FAIL] 'dbo.alembic_version' table is empty or missing.")
                return False
            actual_head = row[0]
            print(f"Verified Database Head: {actual_head}")
            print(f"Expected Repository Head: {EXPECTED_ALEMBIC_HEAD}")

            if actual_head != EXPECTED_ALEMBIC_HEAD:
                print(f"[FAIL] Revision mismatch! Expected {EXPECTED_ALEMBIC_HEAD}, got {actual_head}")
                return False
            print("[PASS] Database migration revision exactly matches repository HEAD.")
    except Exception as exc:
        print(f"[FAIL] Error querying alembic_version: {exc}")
        return False

    print("\n==================================================")
    print("MIGRATION VALIDATION PASSED: DATABASE READY")
    print("==================================================")
    return True


def main():
    parser = argparse.ArgumentParser(description="Safe Staging Migration Validation Tool")
    parser.add_argument(
        "--target-env",
        required=True,
        choices=["staging", "test", "dev", "production"],
        help="Explicit target operating environment (never defaults)",
    )
    parser.add_argument(
        "--database-url",
        default="",
        help="Explicit SQLAlchemy database connection string (overrides environment)",
    )
    parser.add_argument(
        "--force-production-confirmation",
        action="store_true",
        help="Required confirmation flag if target is production",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect connectivity and revision without running upgrade",
    )

    args = parser.parse_args()

    db_url = args.database_url or os.getenv("DATABASE_URL", "")
    if not db_url:
        print("[FAIL] No database URL supplied. Provide --database-url or set DATABASE_URL environment variable.")
        sys.exit(1)

    success = validate_migrations(
        database_url=db_url,
        target_env=args.target_env,
        force_production=args.force_production_confirmation,
        dry_run=args.dry_run,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
