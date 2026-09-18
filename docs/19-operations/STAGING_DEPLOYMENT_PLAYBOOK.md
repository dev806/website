# Staging Deployment Operational Playbook

**Document ID:** `DOC-OPS-001`  
**Phase:** Phase 6.2.5 (Staging & Deployment Validation Foundation)  
**Status:** CANONICAL OPERATIONAL RUNBOOK  
**Governance Notice:** PROPOSED STAGING VALIDATION TOPOLOGY — NOT OWNER APPROVED HOSTING PLATFORM  

---

## 1. Overview & Objective

This playbook defines the exact, sequential operational steps for deploying, migrating, and validating application releases in the **Proposed Isolated Staging SQL Server Environment** prior to any production consideration.

---

## 2. Pre-Deployment Gating Checklist

Before initiating deployment to staging:
* [ ] Working Git tree is clean, and target commit SHA is tagged or identified.
* [ ] All 115+ automated tests pass locally and in GitHub Actions CI against the live Microsoft SQL Server 2022 container.
* [ ] Static analysis is clean: Ruff (0 errors), Bandit (0 security issues), pip-audit (0 vulnerabilities).
* [ ] Staging environment file (`staging.env`) is prepared with a high-entropy 64-character `SECRET_KEY` and dedicated `studio_staging_user` database credentials.
* [ ] Target staging SQL Server instance is reachable via ODBC Driver 18.

---

## 3. Step-by-Step Deployment Procedure

### Step 1: Pre-Migration Database Snapshot / Backup
Execute a native T-SQL compressed backup of the staging database (`StudioWebsiteStag`):
```bash
python scripts/verify_backup_drill.py \
    --database-url "$DATABASE_URL" \
    --database-name "StudioWebsiteStag" \
    --backup-path "/var/backups/mssql/StudioWebsiteStag_predeploy.bak"
```

### Step 2: Code Delivery / Service Update
Pull the target release commit or unpack the deployment artifact on the staging host:
```bash
cd /opt/studio-website
git fetch origin
git checkout <RELEASE_TAG_OR_COMMIT>
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Execute Database Migrations (Safe Runner)
Run the safe migration validation runner targeting staging:
```bash
python scripts/validate_migrations.py \
    --target-env staging \
    --database-url "$DATABASE_URL"
```
*Confirm:* Script outputs `MIGRATION VALIDATION PASSED: DATABASE READY` and verifies Alembic revision `4941998763bd`.

### Step 4: Restart ASGI Service
Restart the multi-worker Uvicorn process under systemd:
```bash
sudo systemctl restart studio-website-staging.service
sudo systemctl status studio-website-staging.service
```

### Step 5: Verify Process & Database Readiness Probes
Confirm process liveness and SQL Server connectivity:
```bash
curl -f http://127.0.0.1:8000/health/live
curl -f http://127.0.0.1:8000/health/ready
```
*Expected Output:*
```json
{"status":"ready","database":{"engine":"Microsoft SQL Server","status":"connected","latency_ms":12.4}}
```

### Step 6: Execute Automated 16-Point Smoke Test Suite
Run the automated staging smoke test runner over HTTPS:
```bash
python scripts/smoke_test.py \
    --base-url "https://staging.studio.internal" \
    --timeout 15 \
    --verbose
```
*Pass Condition:* All 16 checks (SMK-01 through SMK-16) pass 100%.

### Step 7: Post-Deployment Observability Inspection
Inspect host NDJSON log stream to confirm clean request completion and zero unhandled errors:
```bash
journalctl -u studio-website-staging.service -n 50 --no-pager
```
*Audit:* Confirm correlation IDs are present, health probes are logged at DEBUG, and zero PII appears in logs.
