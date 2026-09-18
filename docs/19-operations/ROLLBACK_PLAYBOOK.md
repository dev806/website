# Deployment Rollback Operational Playbook

**Document ID:** `DOC-OPS-002`  
**Phase:** Phase 6.2.5 (Staging & Deployment Validation Foundation)  
**Status:** CANONICAL OPERATIONAL RUNBOOK  
**Governance Notice:** EMERGENCY RECOVERY PROCEDURES  

---

## 1. Overview & Objective

This runbook specifies step-by-step procedures for safely rolling back application code, database migrations, configuration variables, and security secrets in the event of a deployment failure or critical regression.

---

## 2. Reversibility Classification Summary

* **Application Code:** 100% Reversible. Revert to previous Git commit SHA or artifact.
* **Additive Migrations (New Tables / Nullable Columns):** Reversible via `alembic downgrade -1`.
* **Schema Alterations with Data Backfill:** Conditionally reversible. Requires custom tested down-migration script.
* **Destructive DDL (Column / Table Drops):** NOT SAFELY REVERSIBLE via Alembic. Requires full database restore from pre-migration backup.
* **Environment Configuration:** Reversible via environment file restoration and service restart.

---

## 3. Rollback Runbooks

### Runbook A: Application Code Rollback (Zero DB Schema Impact)
If a software bug or regression is detected with zero schema changes:
1. Identify the last known good commit SHA:
   ```bash
   git log -n 5 --oneline
   ```
2. Checkout the previous release:
   ```bash
   git checkout <PREVIOUS_STABLE_SHA>
   ```
3. Restart Uvicorn workers:
   ```bash
   sudo systemctl restart studio-website-staging.service
   ```
4. Execute smoke tests:
   ```bash
   python scripts/smoke_test.py --base-url "https://staging.studio.internal"
   ```

### Runbook B: Additive Database Migration Rollback
If a newly applied additive migration (e.g. newly created table or nullable column) needs to be backed out:
1. Stop incoming traffic or stop application service:
   ```bash
   sudo systemctl stop studio-website-staging.service
   ```
2. Step back one Alembic revision:
   ```bash
   source .venv/bin/activate
   alembic downgrade -1
   ```
3. Confirm revision in database:
   ```bash
   python -c "
   from app.config import get_settings
   from sqlalchemy import create_engine, text
   engine = create_engine(get_settings().get_database_url_str())
   with engine.connect() as c:
       print('Active revision:', c.execute(text('SELECT version_num FROM dbo.alembic_version')).scalar())
   "
   ```
4. Checkout matching previous code version and restart service:
   ```bash
   git checkout <PREVIOUS_STABLE_SHA>
   sudo systemctl start studio-website-staging.service
   ```
5. Run smoke suite to verify system stability.

### Runbook C: Emergency Database Restore (Destructive Schema Rollback)
If destructive DDL occurred or database integrity is compromised:
1. Terminate all active database connections and stop application service:
   ```bash
   sudo systemctl stop studio-website-staging.service
   ```
2. Execute T-SQL restore from pre-deployment backup:
   ```sql
   ALTER DATABASE [StudioWebsiteStag] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
   RESTORE DATABASE [StudioWebsiteStag]
   FROM DISK = '/var/backups/mssql/StudioWebsiteStag_predeploy.bak'
   WITH REPLACE;
   ALTER DATABASE [StudioWebsiteStag] SET MULTI_USER;
   ```
3. Verify integrity:
   ```sql
   DBCC CHECKDB('StudioWebsiteStag');
   ```
4. Start application service and execute smoke test suite.
