# PHASE 6 — DEVOPS, DEPLOYMENT & CI/CD SPECIFICATION

**Document ID:** `DOC-DEV-001`  
**Classification:** DevOps Architecture & Deployment Specification  
**Parent Horizon:** Phase 6 (Rigor, Security & Reliability)  
**Status:** CANONICAL SPECIFICATION — RECONCILED & CORRECTED — AWAITING OWNER APPROVAL  

---

## 1. DEVOPS ARCHITECTURE PHILOSOPHY

The DevOps model of `[STUDIO_NAME]` follows a strict governing constraint: **maintain a lean, reproducible, low-complexity deployment pipeline for a Python/FastAPI + Microsoft SQL Server modular monolith without introducing unnecessary cloud infrastructure or container sprawl**.

---

## 2. CI/CD PIPELINE — SQL SERVER REALITY CHECK

To maintain **100% database dialect fidelity (`BD-001`)**, the CI pipeline does **NOT** replace Microsoft SQL Server with SQLite or PostgreSQL.

The GitHub Actions workflow (`.github/workflows/ci.yml`) utilizes a official Microsoft SQL Server 2022 Linux container service container:

```yaml
# GitHub Actions CI Workflow Specification
name: CI Quality & Security Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mssql:
        image: mcr.microsoft.com/mssql/server:2022-latest
        env:
          ACCEPT_EULA: "Y"
          MSSQL_SA_PASSWORD: "YourPassword123!"
        ports:
          - 1433:1433
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Static Security Scan (Bandit)
        run: bandit -r app/
      - name: Verify Migrations (Alembic)
        run: alembic upgrade head
      - name: Execute Full Test Suite
        env:
          DATABASE_URL: "mssql+pyodbc://sa:YourPassword123!@127.0.0.1:1433/studio_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=no"
        run: |
          pytest tests/ -v
          pytest spikes/test_sprint0_suite.py -v
```

- **Cost**: **$0** (Runs on GitHub Actions free runner minutes).
- **Fidelity**: 100% dialect fidelity against real SQL Server T-SQL engine.

---

## 3. PROVIDER-NEUTRAL PRODUCTION DEPLOYMENT MATRIX

Production hosting selection remains **UNFINALIZED — OWNER DECISION REQUIRED**.

| Deployment Requirement | Azure App Service + Azure SQL | Linux VPS (Hetzner/DO) + SQL Container | AWS Beanstalk + RDS SQL Server |
| :--- | :--- | :--- | :--- |
| **FastAPI / Python 3.13 Support** | Native First-Party | Native | Native |
| **SQL Server Compatibility** | Native Azure SQL Database | Containerized SQL Server | Managed RDS SQL Server |
| **HTTPS / SSL Certificate** | Automated Free Managed Cert | Let's Encrypt / Certbot | AWS ACM |
| **Secrets Management** | Azure Key Vault / App Settings | Systemd Environment File | AWS Secrets Manager |
| **Estimated Monthly Cost** | $15 – $40 / month | $12 – $25 / month | $35 – $60 / month |
| **Operational Complexity** | Low | Medium (Self-managed ops) | Medium |
| **Selection Status** | Candidate Option A | Candidate Option B | Candidate Option C |
| **Final Decision** | **OWNER DECISION REQUIRED** | **OWNER DECISION REQUIRED** | **OWNER DECISION REQUIRED** |

---

## 4. DATABASE BACKUP & RECOVERY STRATEGY

For production database infrastructure (once selected by Owner):
- **Recovery Point Objective (RPO)**: $\le 1$ hour.
- **Recovery Time Objective (RTO)**: $\le 4$ hours.
- **Backup Execution**: Automated daily full backups + hourly transaction log backups.
- **Retention**: 30-day rolling retention for daily backups; encrypted at rest using AES-256.
