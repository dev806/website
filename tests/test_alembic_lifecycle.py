"""
Alembic Migration Lifecycle Integration Tests for [STUDIO_NAME]
Validates upgrade, downgrade, and re-upgrade cycles on Microsoft SQL Server 2022 Express.
"""

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from app.config import get_settings


def test_alembic_upgrade_downgrade_reupgrade(engine):
    """Verifies that the Alembic migration history runs cleanly forward, backward, and forward."""
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")

    # Step 1: Ensure upgrade to head
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "discovery_sessions" in tables
    assert "problem_statements" in tables
    assert "solution_blueprints" in tables
    assert "leads" in tables
    assert "audit_logs" in tables

    try:
        # Step 2: Downgrade to base
        command.downgrade(alembic_cfg, "base")
        inspector_down = inspect(engine)
        tables_down = inspector_down.get_table_names()
        assert "discovery_sessions" not in tables_down
        assert "leads" not in tables_down
    finally:
        # Step 3: Always restore to head for subsequent test modules
        command.upgrade(alembic_cfg, "head")
        inspector_reup = inspect(engine)
        tables_reup = inspector_reup.get_table_names()
        assert "discovery_sessions" in tables_reup
        assert "leads" in tables_reup
