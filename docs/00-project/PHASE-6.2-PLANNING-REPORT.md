# Phase 6.2 — Quality, Testing, DevOps & Observability
## Comprehensive Planning & Governance Audit Report

**Document ID:** `DOC-PLAN-6.2-001`  
**Phase:** Phase 6.2 (Planning & Governance Audit Stage)  
**Status:** COMPLETE — AWAITING OWNER APPROVAL  
**Date:** 2026-09-17  
**Governance Constraint:** Planning Only — Zero Code Modification · Zero Dependency Installation · Zero Schema Changes · ₹0 Infrastructure  

---

## 1. Executive Summary

Phase 6.1 established the security baseline for the AI-Native Technology Studio platform (Security headers, native sliding-window rate limiting on all 7 state-changing POST endpoints, ordered PII/secret scrubbing, SameSite=Lax cookie architecture, and DOC-ARCH-008 error envelopes).

**Phase 6.2 elevates the platform to enterprise engineering rigor** by establishing an automated Quality, Testing, CI/CD, Observability, and Production Readiness foundation.

### Core Governance Principles for Phase 6.2
1. **Fixed Authoritative Architecture:** Python 3.13 · FastAPI · Uvicorn · Jinja2 · HTMX · Alpine.js · SQLAlchemy 2.x · Alembic · Microsoft SQL Server · pyodbc + threadpool · Modular Monolith.
2. **Strict Zero-Bloat Gate:** No PostgreSQL, no SQLite, no Redis, no MongoDB, no vector databases, no React/Next.js, no microservices, no Kubernetes, no commercial AI SDKs, and no multi-agent frameworks.
3. **Real SQL Server Dialect Fidelity (`BD-001`):** CI testing **must** run against real Microsoft SQL Server 2022 (Linux container). SQLite and PostgreSQL substitutions are strictly prohibited.
4. **₹0 Infrastructure Baseline:** Local development remains on SQL Server 2022 Express + Uvicorn. CI utilizes GitHub Actions free runner minutes. Telemetry operates in-house via structured log streams with zero paid SaaS subscriptions.
5. **Provider-Neutral Production:** Production hosting (Azure App Service vs Linux VPS vs AWS) remains **UNFINALIZED — OWNER DECISION REQUIRED**.

---

## 2. Current Empirical Baseline

The codebase was audited to extract exact, unembellished empirical test metrics:

### 2.1 Test Suite Inventory

| Test Module | File Path | Function Count | Pytest Collected Cases | Scope & Subsystem |
| :--- | :--- | :---: | :---: | :--- |
| **Security Hardening** | `tests/test_security.py` | 7 | 7 | Security headers, 429 limiter, exempt routes, PII expansion, SQLi literal handling, XSS escaping, error envelope sanitization |
| **Public Website** | `tests/test_public_website.py` | 9 | 25 | 17 public GET routes (parametrized return 200), 404 handler, robots.txt, sitemap.xml, SEO canonical/OpenGraph, SVG icons, contact POST validation (200 & 422), accessibility landmarks |
| **Discovery FSM** | `tests/test_fsm.py` | 9 | 9 | Linear happy path, fallback engaged, invalid transitions, terminal immutability, blueprint guard, human handoff guard, backtracking, progressive unlock preservation, validation failure recovery |
| **Discovery UX** | `tests/test_discovery_ux.py` | 9 | 9 | Routes structure, fresh session, stage 1 problem error, full 7-stage journey, unlock consent required, unlock invalid email, backtrack to problem/questions, stage 2 radio contract, opportunity map to unlock |
| **Discovery Service** | `tests/test_discovery_service.py` | 7 | 7 | Session lifecycle & persistence, problem submit & PII scrub, short text error, answers submit & map synthesis, lead unlock & blueprint gen, locked access 403, human review handoff |
| **Discovery API** | `tests/test_discovery_api.py` | 4 | 4 | Full discovery API walkthrough, problem validation error, unlock without consent, unauthorized without session |
| **AI Gateway** | `tests/test_ai_gateway.py` | 5 | 5 | PII scrubbing, valid generation, timeout fallback, malformed schema fallback, opportunity map synthesis |
| **Configuration** | `tests/test_config.py` | 4 | 4 | Settings defaults, secret masking (`SecretStr`), database URL resolution, secret key min length |
| **Database Persistence** | `tests/test_database.py` | 3 | 3 | SQL Server live connection, session commit/release, session rollback on error |
| **Data Models** | `tests/test_models.py` | 3 | 3 | Session & problem statement, opportunity & blueprint hierarchy, lead & audit log |
| **Estimation Engine** | `tests/test_estimation.py` | 2 | 2 | Low complexity, high complexity with unknowns & boundary calculations |
| **Health Probes** | `tests/test_health.py` | 3 | 3 | Live probe, ready probe, ready probe database failure simulation |
| **Frontend Templates** | `tests/test_frontend.py` | 2 | 2 | Homepage renders base template, vendored static assets served |
| **Exception Envelopes** | `tests/test_exceptions.py` | 1 | 1 | 404 not found error envelope structure |
| **Alembic Lifecycle** | `tests/test_alembic_lifecycle.py` | 1 | 1 | Full migration upgrade -> downgrade to base -> re-upgrade to head |
| **Sprint 0 Infrastructure** | `spikes/test_sprint0_suite.py` | 7 | 7 | SP-01 (driver packages), SP-02 (live SQL Server), SP-03 (threadpool concurrency), SP-04 (DDL catalog), SP-05 (readiness probe), SP-06 (AI gateway fallback), SP-07 (vendored static assets) |

### 2.2 Baseline Aggregates
- **Application Test Suite (`tests/`):** **15 test modules**, **69 test functions**, **85 collected test cases** (due to 17-path parameterization).
- **Sprint 0 Baseline Suite (`spikes/`):** **1 test module**, **7 test functions**, **7 collected test cases**.
- **Combined Repository Total:** **92 test cases** across 16 test files.
- **Database-Bound Integration Tests:** 31 test cases directly execute queries against live SQL Server (`StudioWebsiteTest`).
- **Pure In-Memory / Route Tests:** 61 test cases run in-memory via FastAPI `TestClient` and mock gateways in **< 1.5 seconds**.

---

## 3. Automated Testing Strategy & Testing Pyramid

To ensure rapid developer feedback without compromising database fidelity, Phase 6.2 formalizes a **4-tier testing pyramid**:

```
                 / \
                / E2E \              Tier 4: Smoke E2E (TestClient / Optional Post-MVP Browser)
               /-------\
              / Security\            Tier 3: Security Regression (Headers, Rate Limiter, PII, XSS, SQLi)
             /-----------\
            / Integration \          Tier 2: SQL Server Integration & Migrations (Real T-SQL Engine)
           /---------------\
          /  Unit & Routes  \        Tier 1: In-Memory Unit, FSM, Routes, & Template Contracts (Sub-Second)
         /-------------------\
```

### 3.1 Tier Breakdown

| Tier | Scope | Target Subsystems | Execution Speed | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Unit & Routes** | In-memory unit & contract tests | FSM (`test_fsm.py`), AI Gateway mocks (`test_ai_gateway.py`), Estimation math (`test_estimation.py`), Config (`test_config.py`), Public routes (`test_public_website.py`) | **< 1.5 seconds** | None (In-memory `TestClient`) |
| **Tier 2: SQL Server Integration** | Dialect & persistence integration | Models (`test_models.py`), Discovery session lifecycle (`test_discovery_service.py`), Alembic lifecycle (`test_alembic_lifecycle.py`), Database pool (`test_database.py`) | **10 – 20 seconds** | Real SQL Server (Local Express or CI Linux Container) |
| **Tier 3: Security Regression** | Security hardening boundaries | Security headers, 5 req/min rate limiter, PII scrubbing catalog, SQLi literal handling, XSS escaping, Error leakage (`test_security.py`) | **< 0.5 seconds** | In-memory |
| **Tier 4: End-to-End Smoke** | Full user journey validation | 7-stage Discovery journey, lead unlock, blueprint rendering, contact submission (`test_discovery_ux.py`) | **< 2.0 seconds** | `TestClient` + DB Session |

### 3.2 Playwright Browser E2E Evaluation

| Evaluation Criteria | Assessment |
| :--- | :--- |
| **Current TestClient Coverage** | FastAPI `TestClient` + Jinja2 context inspection + HTML string assertions currently validate 100% of routes, form payloads, status codes, error states, and security headers in **sub-second time**. |
| **Driver Reliability Risk** | Live testing in Phase 6.1 demonstrated that Playwright browser driver binaries (`playwright-1.57.0-win32_x64.zip`) are vulnerable to upstream CDN 404 download failures. |
| **CI Overhead & Bloat** | Adding Playwright requires Node.js runtime or Python browser driver downloads (>300MB), increasing CI execution times by 2–4 minutes per run. |
| **Architectural Mandate** | The application is a server-rendered Jinja2 + HTMX application with lightweight Alpine.js interactivity, not a complex client-side Single Page Application (SPA). |
| **Definitive Recommendation** | **REJECT Playwright for Current MVP.**<br>• **Current MVP Requirement:** Retain Pytest + FastAPI `TestClient`. It is deterministic, sub-second, ₹0 bloat, and fully validates application behavior.<br>• **Recommended Future Enhancement (Post-MVP):** Evaluate lightweight Playwright smoke tests only if complex client-side canvas interactions, drag-and-drop, or multi-tab browser sessions are introduced in future phases. |

---

## 4. CI/CD Strategy (GitHub Actions)

### 4.1 CI Engine Selection
- **Platform:** GitHub Actions (`ubuntu-latest`).
- **Cost:** **₹0 / $0** (Operates entirely within GitHub Actions free tier for public/standard repositories).
- **Runtime:** Python 3.13.

### 4.2 Core Principles
1. **Dialect Integrity:** No mocks or SQLite substitutions for database tests. CI executes against a real Microsoft SQL Server 2022 Linux container.
2. **Fail-Fast Sequence:** Fast static checks and in-memory unit tests execute before initiating slower database-bound integration tests.
3. **Artifact Retention:** Test logs, code quality reports, and security audit outputs are retained as CI artifacts for failure triage.

---

## 5. SQL Server CI Container Design

### 5.1 Service Container Architecture
In `.github/workflows/ci.yml`:

```yaml
services:
  mssql:
    image: mcr.microsoft.com/mssql/server:2022-latest
    env:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "YourPassword123!"
      MSSQL_PID: "Express"
    ports:
      - 1433:1433
    options: >-
      --health-cmd "/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourPassword123!' -C -Q 'SELECT 1' || exit 1"
      --health-interval 5s
      --health-timeout 3s
      --health-retries 10
```

### 5.2 Practical CI Readiness Requirements
1. **Linux ODBC Driver Installation:** `ubuntu-latest` requires Microsoft's `msodbcsql18` package to enable `pyodbc` connections:
   ```bash
   curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
   curl https://packages.microsoft.com/config/ubuntu/24.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
   sudo apt-get update
   sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
   ```
2. **Readiness Probe:** SQL Server takes 8–15 seconds to initialize system databases. The workflow must poll until TCP port 1433 accepts connections before executing Alembic migrations.
3. **Database Creation Step:** Execute `CREATE DATABASE StudioWebsiteTest;` via `sqlcmd` prior to running migrations.
4. **Connection String in CI:**
   ```
   DATABASE_URL=mssql+pyodbc://sa:YourPassword123!@127.0.0.1:1433/StudioWebsiteTest?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
   ```
5. **Transactional Isolation:** Tests leverage the existing `conftest.py` transactional rollback fixture (`db_session`), ensuring zero test pollution.

---

## 6. Code Quality & Static Analysis Strategy

### 6.1 Tooling Evaluation Matrix

| Tool | Proposed Role | Justification / Value | Overlap with Existing | Complexity Impact | Recommendation | Owner Approval Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **pytest** | Test runner | Already established; runs all 92 tests | None (Baseline) | Zero | **RETAIN** | Approved |
| **Ruff** | Linter & Formatter | Ultra-fast Rust binary; replaces Flake8, Black, isort; catches dead code, unused imports, syntax errors | Replaces 4 disparate tools | Zero runtime overhead | **RECOMMEND** | **Awaiting Approval** |
| **Bandit** | Static Security Analyzer | AST scanner; catches insecure temp files, SQL injection risks, unsafe deserialization | None (Complements pytest) | Dev dependency only | **RECOMMEND** (Deferred in 6.1) | **Awaiting Approval** |
| **pip-audit** | CVE Scanner | Audits `requirements.txt` against PyPA Advisory Database for known vulnerabilities | None | CI-only execution | **RECOMMEND** | **Awaiting Approval** |

### 6.2 Zero-Bloat Gate Analysis
- **Ruff:** Materially improves code hygiene (catches unused imports like `sqlalchemy.text` in `conftest.py` identified in Phase 6.1 audit). Replaces multi-tool configurations with a single `[tool.ruff]` section in `pyproject.toml`.
- **Bandit:** Enforces zero-regression on security boundaries. Scans the AST for raw SQL concatenations or dangerous deserialization before PR merge.
- **pip-audit:** Prevents vulnerable transitive dependencies from slipping into production. Incurs zero runtime overhead.

---

## 7. Observability & Structured Logging Strategy

### 7.1 Governing Principles
- **No Third-Party Paid Monitoring (₹0 Mandate):** No Datadog, New Relic, Sentry, or Grafana Cloud at this stage.
- **Structured Application Log Stream:** Dual formatting via Python's standard `logging` library:
  - Development (`APP_ENV=development`): Human-readable colored console output.
  - Production (`APP_ENV=production`): Structured newline-delimited JSON (NDJSON) output to stdout.
- **Correlation ID Tracking:** Every log record carries `correlation_id` propagated via `contextvars` across the request lifecycle.
- **Security & Privacy Safe:** Automated scrubbing ensures zero API keys, passwords, database credentials, or plain customer PII appear in log streams.

### 7.2 Core Observability Events

| Event Scope | Diagnostic Data Emitted | Target Purpose |
| :--- | :--- | :--- |
| **Request Trace** | `method`, `path`, `status_code`, `duration_ms`, `ip_hash`, `correlation_id` | Traffic monitoring and latency regression tracking |
| **Rate Limit Exceeded** | `ip_hash`, `path`, `limit="5/60s"`, `retry_after=60`, `correlation_id` | Abuse detection and bot identification |
| **Database Diagnostics** | Connection checkout duration, slow query warnings (`duration > 500ms`), pool exhaustion alerts | Persistence health and bottleneck isolation |
| **AI Gateway Diagnostics** | `provider="studio-mock-v1"`, `fallback_engaged=bool`, `latency_ms`, `character_count` | Gateway resilience and fallback circuit tracking |
| **Error Diagnostics** | `error_code`, `message`, `path`, `correlation_id` (Zero raw stack traces in responses) | Exception debugging without information leakage |
| **System Lifecycle** | Engine pool initialization, pool disposal, migration version on boot | Boot sequence verification |

---

## 8. Application Telemetry & Analytics Strategy

### 8.1 Architectural Approach
The platform uses **Custom In-House Telemetry via Structured Application Logs**.
- **No Third-Party Client Scripts:** Zero Google Analytics, Meta Pixel, or Plausible scripts injected into Jinja2 templates (protects customer privacy and eliminates ad-blocker friction).
- **No Database Write Bloat:** Telemetry events are **NOT** written to SQL Server tables (preserves database I/O for business-critical lead and session records).
- **Mechanism:** Asynchronous emission of structured JSON telemetry records to stdout / dedicated log stream.

### 8.2 Anonymous Product Event Taxonomy

| Event Name | Trigger Condition | Emitted Context (Zero PII) |
| :--- | :--- | :--- |
| `discovery_started` | User initiates interactive discovery | `session_token_hash`, `timestamp`, `referrer_domain` |
| `discovery_stage_completed` | User completes any of the 7 stages | `session_token_hash`, `stage_number`, `stage_name`, `dwell_time_sec` |
| `opportunity_map_viewed` | Stage 4 synthesis rendered | `session_token_hash`, `opportunity_count`, `complexity_tier` |
| `blueprint_unlock_started` | User reveals unlock modal | `session_token_hash`, `trigger_source` |
| `blueprint_unlocked` | User successfully unlocks blueprint | `session_token_hash`, `timestamp` *(Name & email sent to `leads` table only, never to telemetry stream)* |
| `estimate_viewed` | User views indicative sizing range | `session_token_hash`, `complexity_tier`, `currency` |
| `contact_submitted` | User submits contact inquiry | `project_scope_category`, `timestamp` *(Zero contact details emitted to telemetry)* |

---

## 9. Provider-Neutral Production Readiness Matrix

| Production Dimension | Current State | Required Production Configuration | Owner Decision Required? |
| :--- | :--- | :--- | :---: |
| **Hosting Platform** | Local Uvicorn | Linux VPS (Caddy/Systemd) vs Azure App Service vs AWS | **YES — OWNER DECISION** |
| **Database Engine** | SQL Server 2022 Express | Azure SQL Database vs Managed SQL Server vs Container | **YES — OWNER DECISION** |
| **Database Connectivity** | Windows Shared Memory | Encrypted TCP/IP with pooled pyodbc connections | No (Architectural standard) |
| **Environment Variables** | Local `.env` | System environment / Key Vault injection | No |
| **Cryptographic Secrets** | Masked default in `app/config.py` | 64+ char random secret key via `SECRET_KEY` | No |
| **Migrations** | Manual `alembic upgrade head` | Automated CI/CD pre-deployment migration step | No |
| **HTTPS / TLS** | HTTP on `127.0.0.1:8000` | Automated Let's Encrypt / Managed Certificate | No |
| **Cookie Security** | `session_secure_cookie=False` | `SESSION_SECURE_COOKIE=True` | No |
| **Security Headers** | Enforced via middleware | Enforced via middleware + reverse proxy | No |
| **Rate Limiting** | In-memory sliding window | Process-local middleware + reverse-proxy edge limiting | No |
| **Logging & Output** | Colored console logs | NDJSON structured logs to stdout | No |
| **Health Probes** | `/health/live`, `/health/ready` | Wired to container orchestrator / uptime monitoring | No |
| **Error Handling** | DOC-ARCH-008 envelopes | Preserved uniform JSON envelopes | No |
| **Static Assets** | Local StaticFiles mount | `Cache-Control: public, max-age=31536000, immutable` | No |
| **Outbound Email** | Mock mode (`SMTP_ENABLED=False`) | Production SMTP gateway (Postmark / SendGrid / Amazon SES) | **YES — OWNER DECISION** |
| **AI Subsystem** | Mock mode (`studio-mock-v1`) | Vetted zero-retention provider vs self-hosted model | **YES — OWNER DECISION** |
| **Domain & DNS** | `localhost:8000` | Custom studio apex & www domain configuration | **YES — OWNER DECISION** |

---

## 10. Test-Data & Environment Strategy

### 10.1 Environment Separation

```
[ DEVELOPMENT ]                     [ TESTING ]                        [ PRODUCTION ]
• Local SQL Server Express           • Dedicated test database           • Dedicated production SQL Server
• DB: StudioWebsiteDev               • DB: StudioWebsiteTest             • DB: [PROD_DB_NAME]
• Mock AI Provider                   • Mock AI Provider                  • Live Vetted AI / Circuit Fallback
• SMTP Disabled                      • SMTP Disabled                     • Live Production SMTP
• Detailed Debug Logs                • Transient Test Fixtures           • NDJSON Structured Output
• session_secure_cookie=False        • autouse rate-limit resets         • session_secure_cookie=True
```

### 10.2 Secret Protection Rules
1. **`.env` Exclusion:** `.env` is strictly git-ignored. Only `.env.example` with non-sensitive placeholder tokens is committed.
2. **Masked Settings:** All passwords and cryptographic keys use Pydantic `SecretStr`, preventing accidental leakage in string serializations or debug traces.
3. **Zero Test Secrets:** Test fixtures never use production credentials.

---

## 11. Documentation Conflict & Drift Audit

| Document | Stale / Conflicting Content | Current Implementation Reality | Classification | Required Action |
| :--- | :--- | :--- | :--- | :--- |
| `DOC-PLAN-6.0-001` (Planning Draft) | Mentioned `/discovery/submit` in legacy table | Replaced by `/discovery/problem`, `/discovery/answers`, `/discovery/unlock`, `/discovery/review` | **Should Fix** | Reconciled in Phase 6.1; align historical references |
| `DOC-DB-001` (Historical Draft) | Referenced PostgreSQL and Prisma ORM | Microsoft SQL Server 2022 + SQLAlchemy 2.x + Alembic | **Historical / Acceptable** | Retained as superseded legacy draft; note in glossary |
| `DOC-WEB-001` (Historical Draft) | Referenced Next.js / React SPA | Python 3.13 + FastAPI + Jinja2 + HTMX + Alpine.js | **Historical / Acceptable** | Retained as superseded legacy draft |
| `DOC-ARCH-016` (Historical Draft) | Referenced Redis + Celery worker queues | Threadpool Async + Synchronous SQL Server | **Should Fix** | Reconcile to zero-Redis architecture |
| `DOC-TEST-001` (Test Baseline) | Historical reference to ~78 tests | Exactly 92 test cases (85 application + 7 Sprint 0) | **Must Fix Before 6.2** | Update test documentation with exact 92 baseline |
| `blueprint/service.py:210` | "Zero-Retention API Integration" copy in template | Mock AI provider currently active | **Deferred** | Validate copy when live AI provider is selected |

---

## 12. Dependency & Tooling Evaluation (Zero-Bloat Gate)

| Proposed Addition | Purpose | License | Runtime Bloat | Cost | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ruff` | Fast static analysis, dead code detection, code formatting | MIT | Dev dependency only (0 production bloat) | ₹0 | **Recommend for Phase 6.2 upon approval** |
| `bandit` | Static security scanner (AST inspection) | Apache 2.0 | Dev dependency only (0 production bloat) | ₹0 | **Recommend for Phase 6.2 upon approval** |
| `pip-audit` | Vulnerability scanning for dependencies | Apache 2.0 | CI/Dev only (0 production bloat) | ₹0 | **Recommend for Phase 6.2 upon approval** |
| `playwright` | Headless browser testing | Apache 2.0 | Heavy binary driver (>300MB), Node dependencies | ₹0 | **REJECT for MVP** (FastAPI TestClient suffices) |
| `slowapi` | Rate limiting | MIT | Redundant with Phase 6.1 native middleware | ₹0 | **REJECT** (Zero dependency baseline achieved) |
| `redis` | In-memory cache / session store | BSD-3 | Requires external daemon, memory overhead, ops bloat | $ / ops | **REJECT** (Violates ₹0 local-first monolith) |

---

## 13. Risk Register & Mitigation Strategy

| Risk ID | Risk Description | Probability | Impact | Mitigation Strategy |
| :--- | :--- | :---: | :---: | :--- |
| **RSK-62-01** | SQL Server Linux container startup delay in CI causing migration timeout | Medium | Medium | Implement polling readiness probe loop (`sqlcmd` check up to 30s) before executing Alembic. |
| **RSK-62-02** | Local Windows Shared Memory pre-login delay (`Timeout error [258]`) during high-frequency tests | Medium | Low | Use session-scoped connection pools and transaction rollbacks rather than recreating engines per test. |
| **RSK-62-03** | PII leakage in application telemetry stream | Low | High | Enforce telemetry event schema validation; drop or hash all customer identifiers before log emission. |
| **RSK-62-04** | Accidental installation of unauthorized dependencies during CI setup | Low | High | Pin dependencies strictly in `requirements.txt`; verify against prohibited dependency checklist. |

---

## 14. Deferred Decisions (Documented for Later Phases)

1. **Bandit Installation:** Deferred in Phase 6.1; formally submitted for owner approval in Phase 6.2.
2. **Ruff Linter & Formatter:** Formally submitted for owner approval in Phase 6.2.
3. **Production Cloud Platform Selection:** Defer until Phase 6.4/Deployment.
4. **Outbound Production SMTP Provider:** Defer until production infrastructure provisioning.
5. **Live Commercial AI Provider Selection:** Defer until production deployment; mock gateway preserves ₹0 development.

---

## 15. Implementation Sequence for Phase 6.2

Upon owner review and approval, Phase 6.2 execution will proceed in four non-breaking sub-phases:

```
Phase 6.2.1 (Tooling & Quality Setup) 
   │  • Configure Ruff & Bandit in pyproject.toml
   │  • Run baseline linter/security scans
   ▼
Phase 6.2.2 (GitHub Actions CI Workflow)
   │  • Author .github/workflows/ci.yml
   │  • Provision SQL Server 2022 container service
   │  • Automate Alembic migration & 92 test execution
   ▼
Phase 6.2.3 (Observability & Telemetry Enrichment)
   │  • Implement NDJSON production log formatter
   │  • Add structured anonymous telemetry emitter
   │  • Instrument slow-query (>500ms) logging probe
   ▼
Phase 6.2.4 (Production Readiness & Health Probing)
      • Add static asset caching header middleware
      • Verify `/health/ready` database diagnostic probe
      • Document complete deployment checklist
```

---

## 16. Owner Decisions Required

Before Phase 6.2 implementation can begin, owner confirmation is required on the following items:

1. **Static Analysis & Security Tooling Approval:**
   - Confirm approval to install `ruff` and `bandit` as development/CI dependencies.
2. **CI Platform Confirmation:**
   - Confirm approval of GitHub Actions using official Microsoft SQL Server 2022 container (`mcr.microsoft.com/mssql/server:2022-latest`) at ₹0 cost.
3. **E2E Tooling Affirmation:**
   - Confirm rejection of Playwright for MVP in favor of the current fast, zero-bloat Pytest + `TestClient` suite.
4. **Telemetry Scope Approval:**
   - Confirm approval of in-house structured logging telemetry (zero third-party scripts, zero database write bloat).

---

## FINAL STATUS

### PHASE 6.2 PLANNING COMPLETE — AWAITING OWNER APPROVAL
