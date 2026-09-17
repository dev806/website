# Local Development Environment Specification (₹0 Infrastructure)

**Document ID:** `DOC-ARCH-020`  
**Classification:** DevOps & Environment / Phase 4 Local Engineering  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Database Architecture](file:///d:/Project_website/docs/05-architecture/05-DATABASE-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Local Development Mandate: ₹0 Cost & Developer Familiarity

In strict accordance with Owner Decisions `BD-015`, `CST-CNF-007`, and `CST-CNF-008`, the local development setup runs **entirely on local developer workstations at ₹0 infrastructure cost**.

The environment requires **zero cloud hosting accounts, zero paid SaaS subscriptions, and zero external database clusters**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LOCAL DEVELOPMENT TECHNOLOGY STACK                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Operating System: Windows 10 / 11 Workstation                                        │
│ • Python Runtime: Python 3.12+ (64-bit)                                                │
│ • Application Framework: FastAPI + Uvicorn (`--reload`) on `localhost:8000`           │
│ • Template & UI Engine: Jinja2 + HTMX (~14KB) + Alpine.js (~15KB) + Vanilla CSS        │
│ • Relational Database: Microsoft SQL Server Developer Edition or SQL Server Express   │
│ • Database Management: SQL Server Management Studio (SSMS)                            │
│ • Database Driver: Microsoft ODBC Driver 18 for SQL Server                             │
│ • Python ORM & Migrations: SQLAlchemy 2.x + Alembic                                    │
│ • Total Monthly Infrastructure Cost: ₹0 / $0                                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites & Local Software Baseline

Before running the application locally, the workstation must have the following free components installed:
1. **Python 3.12+**: Downloaded from official Python repository; added to system `PATH`.
2. **Microsoft SQL Server**:
   - Free Developer Edition or SQL Server Express running on localhost (`(localdb)\MSSQLLocalDB` or standard instance `localhost:1433`).
3. **SQL Server Management Studio (SSMS)**: Free administration GUI for visual schema inspection, query execution, and backup verification.
4. **Microsoft ODBC Driver 18 for SQL Server**: Official driver providing low-latency C-level database connectivity.

---

## 3. Database Initialization Protocol in SSMS

Prior to first application launch, the developer creates two local databases via SSMS:
```sql
-- 1. Create Local Development Database
CREATE DATABASE StudioWebsiteDev;
GO

-- 2. Create Dedicated Local Test Database
CREATE DATABASE StudioWebsiteTest;
GO

-- 3. Enable Read Committed Snapshot Isolation (RCSI)
ALTER DATABASE StudioWebsiteDev SET READ_COMMITTED_SNAPSHOT ON;
ALTER DATABASE StudioWebsiteTest SET READ_COMMITTED_SNAPSHOT ON;
GO
```

---

## 4. Local Environment Configuration (`.env.local`)

A local `.env` file is placed in the project root containing local-only connection variables:
```ini
# Application Core Settings
APP_NAME=[STUDIO_NAME]
APP_ENV=development
DEBUG=True
SECRET_KEY=local-insecure-dev-signing-key-32chars-minimum!!

# Microsoft SQL Server Local Connection (Windows Trusted Connection)
DATABASE_URL=mssql+aioodbc://localhost/StudioWebsiteDev?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes
TEST_DATABASE_URL=mssql+aioodbc://localhost/StudioWebsiteTest?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes

# AI Gateway (Local Mock Mode or Free-Tier Key)
AI_GATEWAY_MODE=mock
AI_PRIMARY_MODEL=gemini-1.5-flash
AI_API_KEY=mock-key-for-local-testing

# Server Port
HOST=127.0.0.1
PORT=8000
```

---

## 5. Execution & Migration Sequence

*(Note: Documentation of command sequences for future execution. Zero commands are executed in this documentation phase).*

```bash
# 1. Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Apply database migrations to StudioWebsiteDev
alembic upgrade head

# 4. Launch FastAPI development server with hot-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 5. Execute automated test suite against StudioWebsiteTest
pytest tests/
```

---

## 6. Windows ODBC Driver Troubleshooting Guide

* **Issue**: `SSL Provider: The certificate chain was issued by an authority that is not trusted.`
  - **Resolution**: In local development without public CA certificates, the connection string must include `TrustServerCertificate=yes` and `Encrypt=no`.
* **Issue**: `Login failed for user...`
  - **Resolution**: Ensure Windows Authentication is enabled in SQL Server properties in SSMS, and user account has `db_owner` rights on `StudioWebsiteDev`.
