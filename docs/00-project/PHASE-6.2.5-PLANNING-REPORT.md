# Phase 6.2.5 — Staging & Deployment Validation Foundation
## Comprehensive Architectural Planning Report

**Document ID:** `DOC-REP-6.2.5-PLAN`  
**Phase:** Phase 6.2.5 (Staging & Deployment Validation Foundation)  
**Status:** PHASE 6.2.5 PLANNING CORRECTED — AWAITING OWNER APPROVAL  
**Date:** 2026-09-18  
**Governance Posture:** Strict Planning Mode — Zero Code, Test, CI, Schema, Migration, or Infrastructure Modifications Authorized  
**Authoritative Baseline:** Python 3.13 · FastAPI 0.141.1 · Uvicorn 0.52.4 · Jinja2 3.1.6 · HTMX · Alpine.js · SQLAlchemy 2.0.52 · pyodbc 5.3.0 · Microsoft SQL Server 2022 · Microsoft ODBC Driver 18 · Alembic 1.19.2 (Head: `4941998763bd`) · Modular Monolith · Provider-Neutral AI Gateway · NDJSON Observability  

---

## Executive Summary & Phase Purpose

The primary objective of **Phase 6.2.5: Staging & Deployment Validation Foundation** is to establish an exhaustive, evidence-based architectural blueprint that details exactly how the studio platform will be deployed, configured, operated, and validated in a production-identical **Staging Environment** prior to any production launch.

Following the successful remote verification, owner approval, and formal closure of **Phase 6.2.4 (Production Readiness & Deployment Foundation)**, the project operates under strict governance laws:
1. **Planning Only:** No cloud resources, servers, infrastructure, code, tests, CI workflows, migrations, or database schemas are altered during this phase.
2. **Architecture Decoupling:** Development infrastructure remains strictly **₹0 (Windows + Microsoft SQL Server Express + SSMS + local Uvicorn)**. Production hosting and database options remain intentionally open, unfinalized, and vendor-neutral.
3. **No Unapproved Dependencies:** Existing architectural exclusions remain permanently binding: **No PostgreSQL, SQLite, MongoDB, Redis, Kafka, Celery, vector databases, microservices, React/Next.js as primary frontend, or third-party analytics SaaS**.
4. **Prior Phases Immutable:** Phases 5.3 through 6.2.4 remain 100% verified and intact.

This planning report addresses all 24 required dimensions to ensure that staging validation is completely decoupled from guesswork, premature commitments, or unverified provider lock-in.

---

## Mandatory Pre-Planning Repository Audit

A comprehensive pre-planning audit of the live repository was conducted on 2026-09-18. The findings below form the empirical foundation of this report.

### 1. Git Repository State
* **Current Working Branch:** `main`
* **Current HEAD Commit:** `e48a1bd` (`docs: finalize Phase 6.2.4 implementation report with live CI verification`)
* **Recent Commits:**
  * `e48a1bd` — docs: finalize Phase 6.2.4 implementation report with live CI verification
  * `7d79d57` — feat(devops): Phase 6.2.4 production readiness & deployment foundation
  * `b17e196` — docs: finalize Phase 6.2.3 implementation report with live CI verification
* **Remote Tracking:** Synchronized with `origin/main` (GitHub repository).
* **Working Tree Cleanliness:** `nothing to commit, working tree clean` verified via `git status`.

### 2. Test & Verification Baseline
* **Total Collected Tests:** 115 passing tests (100% pass rate).
  * Main Application Test Suite (`tests/`): 108 tests.
  * Sprint 0 Baseline Regression Suite (`spikes/test_sprint0_suite.py`): 7 tests.
* **Remote CI Pipeline:** Verified clean on GitHub Actions (Run ID: `35329057425`, Job ID: `105548890875`, Commit: `7d79d57`) executing against real containerized Microsoft SQL Server 2022 Linux (`mcr.microsoft.com/mssql/server:2022-latest`) and Microsoft ODBC Driver 18.
* **Static Analysis:** Ruff (0 errors), Bandit (0 security issues), pip-audit (0 known vulnerabilities).
* **Active Alembic Head:** `4941998763bd` (Initial MVP Foundation — 10 relational tables in `dbo`).

### 3. Implementation Inspection
* **`app/main.py`:** Configured with Starlette LIFO middleware chain: Request Correlation ID & Performance Telemetry (outermost), Native Security Headers (middle), Native In-Memory Rate Limiting & 1MB Request Payload Defense (innermost). Client IP extraction incorporates `trusted_proxies` filtering to prevent `X-Forwarded-For` spoofing. Static assets mounted at `/static`.
* **`app/config.py`:** Pydantic v2 Settings enforcing fail-fast validation in `validate_production_settings` when `app_env == "production"` (prohibits `debug=True`, dev secret keys, unencrypted cookies, and local `SQLEXPRESS` instances).
* **`app/database/connection.py`:** SQLAlchemy 2.x engine management with thread-pool connection pooling (`pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True`) and cursor execution listeners detecting slow queries (>500ms).
* **`app/ai_gateway/`:** Decoupled `IAIProvider` protocol and `AIServiceGateway` orchestrator with pre-transit PII sanitization, 10s timeout bounding, structured DTO validation, deterministic fallback catalog, and anonymous NDJSON telemetry.
* **`app/routers/web.py`:** Serves approved 7-section homepage narrative, 5 capability pillars, solutions index, methodology, about, privacy/terms/security, dynamic XML sitemap, and `/contact` intake.
* **`app/routers/discovery_views.py` & `app/modules/discovery/router.py`:** Implements 7-stage interactive consultative discovery workflow with progressive unlock, stateless HMAC-SHA256 session cookies (`studio_session_id`), and raw token header suppression in production mode.

### 4. Authoritative vs. Stale Documentation Audit
* **Authoritative Documents:**
  * [`docs/00-project/PHASE-6.2.4-IMPLEMENTATION-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.2.4-IMPLEMENTATION-REPORT.md)
  * [`docs/00-project/PHASE-6.2.4-PLANNING-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.2.4-PLANNING-REPORT.md)
  * [`docs/00-project/PROJECT_CONSTRAINTS.md`](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md)
  * [`docs/00-project/DECISION_LOG.md`](file:///d:/Project_website/docs/00-project/DECISION_LOG.md)
* **Drifted / Stale Documentation Identified:**
  * `docs/05-architecture/22-DEVOPS-AND-DEPLOYMENT.md`: Mentions Python 3.12 (`FROM python:3.12-slim`) and early Gunicorn worker references; the actual verified baseline is Python 3.13 with native Uvicorn.
  * `docs/05-architecture/05-DATABASE-ARCHITECTURE.md` & `06-DATABASE-SCHEMA-SPEC.md`: Drafted prior to Phase 6.2.1; lacked the exact index nomenclature (`ix_audit_logs_event_type`, `ix_leads_corporate_email`) and constraint names established in migration `4941998763bd`.
  * `docs/04-website/13-ANALYTICS-AND-CONVERSION-TRACKING.md`: Contained early discussion of third-party SaaS analytics prior to binding architectural exclusion in favor of in-house NDJSON telemetry (Phase 6.2.3).

---

## Section 1 — Staging Objective

### 1.1 Definition of Staging
For this project, **Staging** is defined as an isolated environment designed to validate the runtime behavior, security boundaries, networking topology, database persistence, and operational procedures of the application under production-like conditions **before** serving public traffic.

Staging is neither a development sandbox nor a test runner. It must mimic target production behavior with high fidelity to ensure that configuration errors, network timeouts, cookie permission bugs, proxy header mismatches, or migration failures are caught without business risk.

The project explicitly differentiates between four separate environments:
1. **Current Development Environment:** Microsoft SQL Server 2022 Express on local Windows workstation with SSMS, Uvicorn in reload mode, mock AI, and ₹0 initial infrastructure cost.
2. **CI Ephemeral Environment:** Ephemeral Microsoft SQL Server 2022 Linux container on GitHub Actions runner with pyodbc and ODBC Driver 18, headless test execution, with fresh databases (`StudioWebsiteDev`, `StudioWebsiteTest`) created and destroyed per run.
3. **Proposed Isolated Staging SQL Server Environment:** Dedicated staging SQL Server instance/database (`StudioWebsiteStag`) containing purely synthetic test data (zero production data, zero replication topology), validating multi-worker process concurrency, reverse proxy ingress, real TLS, and migration safety.
4. **Future Production SQL Server Environment:** Hardened SQL Server instance/PaaS database containing live client records, commercial inquiry persistence, and owner-approved commercial credentials.

### 1.2 Multi-Tier Environment Comparison

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       MULTI-TIER ENVIRONMENT COMPARISON MATRIX                                   │
├───────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┤
│ DIMENSION         │ DEVELOPMENT          │ CI (CONTINUOUS INT.) │ STAGING              │ PRODUCTION              │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Primary Purpose   │ Rapid local coding & │ Automated regression │ Staging operational  │ Serving live commercial │
│                   │ feature design       │ & security gating    │ validation           │ visitors and clients    │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Infrastructure    │ Local Windows Host   │ GitHub Actions Linux │ Linux Server / PaaS  │ Hardened Cloud Host /   │
│                   │ (₹0 initial cost)    │ Ubuntu Runner        │ (Isolated VPC)       │ Managed Cloud PaaS      │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Process Model     │ Single Uvicorn       │ Headless Pytest      │ Multi-worker Uvicorn │ Uvicorn multi-worker    │
│                   │ process (--reload)   │ test runner          │ (Validation cand.)   │ (Empirically establ.)   │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Ingress & TLS     │ Direct HTTP          │ N/A (Internal loop)  │ Reverse Proxy + Real │ Reverse Proxy + Real    │
│                   │ (http://localhost)   │                      │ TLS (Let's Encrypt)  │ TLS + Edge CDN/WAF      │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Database Engine   │ Current: MS SQL 2022 │ CI Ephemeral: MS SQL │ Proposed Isolated    │ Future Production       │
│                   │ Express (Local ₹0)   │ 2022 Linux Container │ Staging SQL Server   │ SQL Server Environment  │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Database Access   │ Windows Trusted Conn │ SQL SA (Container)   │ Dedicated DB User    │ Dedicated DB User       │
│                   │ or SA / SSMS         │ (Internal CI net)    │ (Restricted DBO)     │ (Restricted DBO, SSL)   │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Data Posture      │ Ephemeral scratch /  │ Fresh ephemeral DBs  │ Synthetic test data  │ Live client data &      │
│                   │ local dev records    │ per CI workflow run  │ (Zero production PII)│ commercial inquiries    │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ AI Gateway        │ MockAIProvider       │ MockAIProvider       │ MockAIProvider /     │ Owner-Approved          │
│                   │ (Deterministic)      │ (Deterministic)      │ Sandboxed Provider   │ Commercial AI Provider  │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Email Dispatch    │ Disabled (SMTP=False)│ Disabled (SMTP=False)│ Mock Dispatcher /    │ Owner-Approved          │
│                   │                      │                      │ Mailhog Sandbox      │ Transactional Vendor    │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Access Control    │ Open local loopback  │ Restricted CI agent  │ Restricted (VPN / IP │ Open Public Internet    │
│                   │ (127.0.0.1:8000)     │ runner execution     │ allowlist / BasicAuth│ (Global HTTPS)          │
├───────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ Public SEO Index  │ Disallow / Local     │ Disallow / Ephemeral │ Disallow All         │ Allow / XML Sitemap     │
│                   │                      │                      │ (noindex, nofollow)  │ (Search Index Active)   │
└───────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘
```

---

## Section 2 — Staging Architecture

### 2.1 Provider-Neutral Logical Architecture Flow

> [!IMPORTANT]
> **PROPOSED STAGING VALIDATION TOPOLOGY — NOT OWNER-APPROVED**  
> The logical flow below defines what staging should validate, not an already-selected or approved production hosting architecture. All hosting infrastructure remains decoupled and subject to explicit owner decisions.

```
[ Browser / Client ]
        │
        │ (HTTPS / TLS 1.3 on Port 443)
        ▼
┌──────────────────────────────────────────────────────────┐
│      PROPOSED INGRESS / REVERSE PROXY LAYER              │
│ (Proposed Staging Validation Ingress — Not Owner-Approved│
│             (Caddy / Nginx / Traefik)                    │
│  - Automated ACME TLS Termination (Let's Encrypt)        │
│  - HTTP -> HTTPS 301 Permanent Redirect                  │
│  - HSTS, CSP, and Perimeter Defense Headers              │
│  - Static Asset Offload (/static, 1-year immutable cache)│
│  - Edge Client IP Header Injection (X-Forwarded-For)     │
│  - Edge Coarse Rate Limiting (DDoS Protection)           │
│  - 1MB Request Payload Boundary Check                    │
└──────────────────────────┬───────────────────────────────┘
                           │
                           │ (HTTP/1.1 on Internal Loopback: 127.0.0.1:8000)
                           ▼
┌──────────────────────────────────────────────────────────┐
│         FASTAPI APPLICATION RUNTIME                      │
│ (Proposed Multi-Worker Validation: e.g. 2 workers        │
│  to validate concurrency — Not Approved Prod Count)      │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Starlette Middleware Pipeline                      │  │
│  │  1. Correlation ID Middleware (X-Correlation-ID)   │  │
│  │  2. Security Headers Middleware (Nosniff, Deny)    │  │
│  │  3. Trusted Proxy & IP Extraction (_get_client_ip) │  │
│  │  4. Native Rate Limiter & 1MB Payload Defense      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Web & API Route Modules                            │  │
│  │  - Public Web Views (/services, /contact, /about)  │  │
│  │  - Consultative Discovery UX (/discovery/*)        │  │
│  │  - Discovery REST API (/api/v1/discovery/*)        │  │
│  │  - Health Probes (/health/live, /health/ready)     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Subsystems & Shared Core                           │  │
│  │  - In-Memory Discovery State Machine (7 Stages)    │  │
│  │  - Stateless HMAC Session Signer & Verifier        │  │
│  │  - AI Service Gateway (Pre-transit PII Scrubbing)  │  │
│  │  - Structured NDJSON Observability & Telemetry     │  │
│  └────────────────────────────────────────────────────┘  │
└────────────┬──────────────────┬──────────────────┬───────┘
             │                  │                  │
             │ (SQLAlchemy 2.x) │ (Stdout Stream)  │ (Async HTTP)
             ▼                  ▼                  ▼
┌──────────────────────┐ ┌───────────────┐ ┌──────────────────────┐
│ PERSISTENCE LAYER    │ │ OBSERVABILITY │ │ EXTERNAL INTEGRATIONS│
│ Proposed Isolated    │ │ Structured    │ │                      │
│ Staging SQL Server   │ │ NDJSON Stream │ │ [AI Gateway Adapter] │
│ Environment (2022)   │ │ to stdout     │ │ -> MockAIProvider    │
│                      │ │               │ │    (Staging baseline)│
│ - Database:          │ │ - Correlated  │ │ -> Future LLM Vendor │
│   StudioWebsiteStag  │ │   request logs│ │    (Owner unapproved)│
│ - ODBC Driver 18     │ │ - Slow queries│ │                      │
│ - TLS Encryption     │ │ - Telemetry   │ │ [Email Dispatcher]   │
│ - Dedicated User     │ │   events      │ │ -> Mock / Mailhog    │
│ - Connection Pool    │ │ - Zero PII    │ │ -> Future Transaction│
│   (Budgeted)         │ │               │ │    Email Vendor      │
│ - Alembic Migrations │ │               │ │                      │
│ (Zero Production     │ │               │ │                      │
│  Replication/Data)   │ │               │ │                      │
└──────────────────────┘ └───────────────┘ └──────────────────────┘
```

### 2.2 Governance Component Classification

To prevent unauthorized scope creep, all architecture elements are strictly categorized:

| Component | Governance Status | Rationale |
| :--- | :---: | :--- |
| **FastAPI Core & Routing** | **CURRENTLY VERIFIED** | Implemented, locally verified, and CI tested across 115 tests. |
| **SQLAlchemy 2.x & pyodbc** | **CURRENTLY VERIFIED** | Validated against Microsoft SQL Server 2022 in CI. |
| **Alembic Migration Engine** | **CURRENTLY VERIFIED** | Head `4941998763bd` verified on live SQL Server container. |
| **Trusted Proxy IP Defense** | **CURRENTLY VERIFIED** | Hardened in Phase 6.2.4; tested via `tests/test_production_readiness.py`. |
| **Stateless HMAC Sessions** | **CURRENTLY VERIFIED** | Validated across multiple simulated requests. |
| **NDJSON Logging & Telemetry**| **CURRENTLY VERIFIED** | Phase 6.2.3 approved implementation active. |
| **AI Gateway Contract & Mock**| **CURRENTLY VERIFIED** | `IAIProvider` protocol and fallback catalogs operational. |
| **Ingress Reverse Proxy Config**| **PROPOSED STAGING VALIDATION REQUIREMENT — NOT OWNER-APPROVED** | Proposed staging validation requirement for TLS termination and header forwarding. |
| **Multi-Worker Process Model** | **PROPOSED STAGING VALIDATION REQUIREMENT — NOT OWNER-APPROVED** | Proposed staging validation requirement to test multi-worker concurrency. |
| **Staging SQL Server Host** | **PROPOSED ISOLATED STAGING ENVIRONMENT — NOT OWNER-APPROVED** | Dedicated staging database instance required for non-ephemeral validation. |
| **Multi-Worker Rate Limiting**| **REQUIRES VALIDATION**| Process-local limiter must be validated across multiple workers. |
| **Real TLS & Cookie Scope** | **REQUIRES VALIDATION**| Must be empirically verified in a real browser over HTTPS. |
| **Transient DB Reconnection** | **REQUIRES VALIDATION**| `pool_pre_ping` must be validated against network drops. |
| **Cloud Hosting Platform** | **OWNER DECISION REQUIRED**| Azure App Service vs. Azure Container Apps vs. Linux VPS. |
| **Commercial AI Provider** | **OWNER DECISION REQUIRED**| Selection and budget unfinalized. |
| **Transactional Email Provider**| **OWNER DECISION REQUIRED**| Vendor selection unfinalized. |
| **Staging Subdomain & DNS** | **OWNER DECISION REQUIRED**| Exact staging domain/hostname unassigned. |

---

## Section 3 — Staging Environment Matrix

The detailed operational comparison across all 20 environment parameters is established below:

| Area | Development | CI | Staging | Production |
| :--- | :--- | :--- | :--- | :--- |
| **Application Runtime** | Python 3.13 via venv | Python 3.13 via actions/setup-python | Python 3.13 via OCI container or systemd venv | Hardened Python 3.13 OCI container or systemd venv |
| **Process Model** | Uvicorn single process (`--reload`) | Pytest test execution (ephemeral) | Uvicorn multi-worker (Validation candidate) | Uvicorn multi-worker (Empirically established) |
| **Database Engine** | Current: MS SQL 2022 Express (Local ₹0) | CI Ephemeral: MS SQL 2022 Linux Container | Proposed Isolated Staging SQL Server Environment | Future Production SQL Server Environment |
| **Database Credentials** | Windows Integrated / `sa` default | `sa` default (`YourStrong!Password123`) | Dedicated `studio_staging_user` (restricted DBO) | Dedicated `studio_prod_user` (least privilege DBO) |
| **Session Secret Key** | Dev insecure default string | CI temporary test string | High-entropy 64-char cryptographically random | High-entropy 64-char cryptographically random |
| **Session Cookies** | `secure=False`, `httponly=True`, `samesite=lax` | N/A (TestClient programmatic) | `secure=True`, `httponly=True`, `samesite=lax` | `secure=True`, `httponly=True`, `samesite=lax` |
| **HTTPS / TLS** | None (`http://localhost:8000`) | None (Local socket) | Full TLS 1.2/1.3 via automated Let's Encrypt | Full TLS 1.2/1.3 via commercial / automated TLS |
| **Reverse Proxy** | Direct connection (None) | None | Proposed Caddy or Nginx reverse proxy | Caddy, Nginx, or Cloud Ingress + WAF |
| **Proxy Trust Setting** | `TRUSTED_PROXIES=127.0.0.1,::1` | `TRUSTED_PROXIES=testclient` | `TRUSTED_PROXIES=127.0.0.1` (or internal proxy IP) | `TRUSTED_PROXIES=<Ingress_VPC_Subnet_IPs>` |
| **Rate Limiting** | In-process (5 req/min) | In-process (validated in tests) | Edge reverse proxy + In-process multi-worker | Edge reverse proxy (WAF) + In-process defense |
| **AI Provider** | `MockAIProvider` (deterministic) | `MockAIProvider` (deterministic) | `MockAIProvider` (or sandboxed LLM test key) | Owner-approved Commercial LLM Provider API |
| **Email Dispatcher** | `SMTP_ENABLED=False` | `SMTP_ENABLED=False` | Mock dispatcher / Mailhog sandbox | Owner-approved Transactional Email API/SMTP |
| **Logging Format** | Text format (`log_format="text"`) | Standard stdout | NDJSON format (`log_format="json"`) | NDJSON format (`log_format="json"`) |
| **Telemetry** | Anonymous local events (stdout) | Validated in test assertions | Anonymous events to stdout (filtered noise) | Anonymous events to stdout (aggregated) |
| **Data Posture** | Scratch dev sessions & tests | Fresh ephemeral DB per run | Synthetic test sessions (zero client PII) | Real customer discovery & commercial leads |
| **Migration Posture** | Manual `alembic upgrade head` | Automated in CI step | Pre-start automated deployment gate | Strict Expand/Contract deployment pipeline |
| **Deployment Model** | Manual developer execution | Automated GitHub Actions | Automated / scripted to staging server | Blue/Green or rolling worker restart |
| **Access Control** | Unrestricted local machine | Repository push permissions | Restricted: VPN / IP allowlist / BasicAuth | Public Internet (Open HTTPS) |
| **Backups & DR** | Local developer discretion | None (Ephemeral CI runner) | Daily automated full backup + restore drills | Daily full + hourly differential + off-site storage |
| **Monitoring** | Terminal output | CI step pass/fail | Health probe polling + host resource metrics | 24/7 uptime ping + error rate alert thresholds |
| **Domain & DNS** | `localhost:8000` | None | Staging subdomain (e.g. `staging.domain.com`) | Production apex & `www` canonical domain |

---

## Section 4 — Deployment Packaging Analysis

### 4.1 Standalone Application Audit
An audit of the existing codebase confirms that the application is fully functional as a standalone ASGI service:
* **Entry Point:** `app.main:app`, manufactured via `create_app()` factory.
* **CLI Startup Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` (illustrative validation command; staging should validate multi-worker behavior, while final production worker/process count requires empirical capacity validation and owner/hosting decision).
* **Static Assets:** Mounted natively via `StaticFiles(directory="static")` in `app/main.py`.
* **Templates:** Loaded from `templates/` via Jinja2 template loader.
* **Database Engine Lifecycle:** Engine is warmed up at startup during FastAPI `lifespan` and disposed cleanly via `dispose_engine()` on shutdown.
* **Graceful Shutdown:** Tested and responsive to standard POSIX `SIGTERM` / `SIGINT` signals.

### 4.2 Deployment Packaging Options: Bare-Metal vs. Containerization

The architecture evaluated two neutral packaging strategies without committing prematurely to either:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DEPLOYMENT PACKAGING EVALUATION                                 │
├─────────────────────────┬───────────────────────────────────┬───────────────────────────────────┤
│ CRITERIA                │ OPTION 1: BARE-METAL LINUX HOST   │ OPTION 2: OCI CONTAINER (DOCKER)  │
│                         │ (systemd + Python venv)           │ (Minimal Multi-Stage Image)       │
├─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│ Dependency Isolation    │ Relies on host OS package manager │ 100% self-contained filesystem;   │
│                         │ (apt for ODBC Driver 18).         │ ODBC Driver 18 baked in.          │
├─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│ Parity with CI Baseline │ Diverges from CI (CI runs in      │ 100% parity with GitHub Actions   │
│                         │ containerized Linux runner).      │ and SQL Server container model.   │
├─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│ Compute Overhead        │ Zero container overhead; direct   │ Negligible Linux namespace        │
│                         │ kernel thread scheduling.         │ overhead (~10–20MB RAM).          │
├─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│ Cloud Portability       │ Tied to VPS / VM architecture.    │ Runs identically on VPS, Azure    │
│                         │ Requires custom deploy scripts.   │ Container Apps, App Service, etc. │
├─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│ Operational Complexity  │ Requires host-level Python & ODBC │ Requires container registry and   │
│                         │ maintenance.                      │ container engine (Docker/Podman). │
├─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┤
│ Architecture Status     │ FEASIBLE CANDIDATE                │ RECOMMENDED CANDIDATE             │
└─────────────────────────┴───────────────────────────────────┴───────────────────────────────────┘
```

**Neutral Recommendation:** While bare-metal systemd execution is completely viable, an OCI-compliant container packaging provides the highest reproducibility and matches the verified GitHub Actions CI environment. However, **no Dockerfiles or container images are created during this planning phase**. Staging should validate multi-worker behavior; the final production worker/process count requires empirical capacity validation and owner/hosting decision.

---

## Section 5 — Reverse Proxy & HTTPS Ingress Requirements

### 5.1 Ingress Requirements Specification
> [!NOTE]
> **PROPOSED STAGING VALIDATION TOPOLOGY — NOT OWNER-APPROVED**  
> The requirements below define what staging ingress should validate to simulate production conditions (TLS termination, HTTPS redirect, HSTS, forwarded headers, edge rate limiting), rather than prematurely selecting or approving a final hosting architecture.

The staging environment requires an edge reverse proxy (such as Caddy, Nginx, or Traefik) positioned in front of Uvicorn. The reverse proxy must satisfy the following provider-neutral requirements:

1. **TLS Termination:**
   * Support TLS 1.2 and TLS 1.3 only; disable SSLv3, TLS 1.0, and TLS 1.1.
   * Automated certificate issuance and renewal via ACME (Let's Encrypt / ZeroSSL).
2. **HTTP Redirection:**
   * All cleartext HTTP traffic arriving on port 80 must return an immediate HTTP 301 redirect to `https://<host>:<port>`.
3. **Forwarded Header Injection:**
   * The proxy must inject standard proxy headers:
     * `X-Forwarded-For`: Appending the true remote client IP address.
     * `X-Forwarded-Proto`: Set strictly to `https`.
     * `X-Forwarded-Host`: Preserving original requested host.
     * `Host`: Preserving the target hostname.
4. **Trusted Proxy Handshake:**
   * The reverse proxy IP address must match the application's `TRUSTED_PROXIES` setting so that FastAPI's `_get_client_ip()` extracts the true remote IP and prevents client IP spoofing.
5. **Static Asset Caching:**
   * The reverse proxy should serve `/static/*` files directly from disk, setting `Cache-Control: public, max-age=31536000, immutable` for versioned assets, offloading Python worker threads.
6. **Perimeter Payload Defense:**
   * Reverse proxy must enforce a maximum client body size of 1MB (`client_max_body_size 1m`), mirroring FastAPI's internal boundary and shedding oversized payloads before they reach Python.
7. **Perimeter Rate Limiting:**
   * Coarse IP-based rate limiting (e.g. 20 requests per second per IP) to absorb automated scanning and volumetric denial-of-service attempts.
8. **Timeouts:**
   * Ingress proxy timeout must be configured to at least 15 seconds to allow the application's 10-second AI Gateway timeout to complete and return a graceful fallback response before the proxy cuts the connection.

---

## Section 6 — Multi-Worker Validation

### 6.1 Process-Local Rate Limiting vs. Multi-Worker Scaling
Phase 6.2.4 established that:
1. Session management is **completely stateless**: `studio_session_id` cookies are cryptographically signed using HMAC-SHA256 (`SECRET_KEY`). Any worker process holding `SECRET_KEY` can independently verify the cookie, hash the token with SHA-256, and lookup the session in `dbo.discovery_sessions`.
2. Discovery progress is **completely durable**: All stage transitions and state variables are persisted in Microsoft SQL Server.
3. Current rate limiting is **process-local**: `_rate_limit_store` in `app/main.py` is an in-memory dictionary local to each Python process.

**Multi-Worker Validation Principle:** Staging should validate multi-worker behavior; the final production worker/process count requires empirical capacity validation and owner/hosting decision.

### 6.2 Multi-Worker Implications

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-WORKER ARCHITECTURAL BEHAVIOR ANALYSIS                             │
├─────────────────────┬──────────────────────────┬─────────────────────────────────────────────────┤
│ SYSTEM COMPONENT    │ 1 WORKER (DEV/TEST)      │ MULTI-WORKER (STAGING / PRODUCTION CANDIDATE)   │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Session State       │ Stateless & DB-backed;   │ Identical. Requests can hit Worker A then       │
│                     │ works seamlessly.        │ Worker B with zero session loss.                │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Request Correlation │ Independent per request; │ Independent per request; isolated in Python     │
│                     │ `contextvars` context.   │ thread/task context across all worker processes.│
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Rate Limiting       │ Exact: 5 requests / 60s  │ Partitioned: Each worker tracks its own memory  │
│ (In-Process)        │ per IP on target routes. │ store. An IP could theoretically make up to     │
│                     │                          │ N_workers * 5 requests/min across round-robin.  │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Logging & Telemetry │ Synchronous stdout;      │ Multiplexed stdout; handled cleanly by host     │
│                     │ single stream.           │ process supervisor (systemd journal or Docker). │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Database Connection │ Pool: 10 base, 20 max    │ Total Connections = N_workers * (10 + 20)       │
│ Budgeting           │ = 30 max connections.    │ For 2 validation workers = 60 max connections.  │
└─────────────────────┴──────────────────────────┴─────────────────────────────────────────────────┘
```

### 6.3 Resolution of the Distributed Rate Limiting Question
Architectural governance strictly forbids introducing **Redis** or other external in-memory stores. To resolve rate limiting without Redis, the architecture clearly distinguishes three tiers:
1. **Current Application-Level Defense-in-Depth Rate Limiting:** The process-local sliding window (`_rate_limit_store` in `app/main.py`) which continues to protect individual worker event loops from thread exhaustion.
2. **Proposed Staging Edge Rate Limiting:** Coarse rate limiting at the staging reverse proxy layer (e.g., Caddy / Nginx) to validate perimeter defense against high-frequency traffic across multiple workers without shared memory.
3. **Future Production Distributed/Edge Rate Limiting:** Production edge WAF or CDN rate limiting (e.g., Cloudflare / Azure Front Door) configured in accordance with the owner's eventual hosting decision.

**Redis is strictly excluded** by architectural governance and will not be introduced.

---

## Section 7 — Database Deployment & Compatibility Validation

### 7.1 Database Engine Compatibility & Environment Distinction
The application relies on Microsoft SQL Server 2022. The repository distinguishes four database environments:
* **Current Development:** Local MS SQL Server 2022 Express instance on Windows with SSMS (₹0 cost).
* **CI Ephemeral:** Containerized MS SQL Server 2022 Linux on GitHub Actions runners, destroyed post-run.
* **Proposed Isolated Staging SQL Server Environment:** Dedicated staging SQL Server database (`StudioWebsiteStag`) provisioned purely for staging validation with synthetic data (zero production data, zero replication topology).
* **Future Production SQL Server Environment:** Hardened SQL Server environment (Linux VPS or Azure SQL) hosting live commercial data.

Staging must validate connectivity against:
1. **Engine Target:** Microsoft SQL Server 2022 (Linux container or Windows host) or Azure SQL Database (General Purpose vCore or Basic/Standard DTU).
2. **Client Driver:** Microsoft ODBC Driver 18 for SQL Server (`Driver={ODBC Driver 18 for SQL Server}`).
3. **Transport Security:**
   * Local Dev: `TrustServerCertificate=yes` (self-signed dev certificate).
   * Staging / Production: `Encrypt=yes;TrustServerCertificate=no` with proper CA verification or Azure SQL trusted certificates.
4. **Authentication:** Dedicated database user account (`studio_staging_user`) granted explicit `db_datareader`, `db_datawriter`, and `db_ddladmin` permissions on `StudioWebsiteStag`. **Never run application workloads under `sa`**.

### 7.2 Connection Pool Sizing Math
SQLAlchemy connection pooling in `app/database/connection.py` uses:
* `database_pool_size = 10`
* `database_max_overflow = 20`
* `database_pool_recycle = 1800` (30 minutes)
* `pool_pre_ping = True`

**Pool Budgeting Formulation:**
$$\text{Max DB Connections} = \text{Worker Count} \times (\text{database\_pool\_size} + \text{database\_max\_overflow})$$
* For an illustrative staging validation setup of 2 workers: $2 \times (10 + 20) = 60\text{ maximum connections}$.
* Staging database configuration must verify that SQL Server's `user connections` setting comfortably exceeds this budget, and database memory is budgeted accordingly.
* *Note:* Final production connection pool sizing depends on empirical capacity testing and the owner's selected database compute tier.
* `pool_pre_ping=True` ensures stale connections terminated by cloud firewalls or network idle drops are automatically discarded and re-established without throwing HTTP 500 errors to clients.

---

## Section 8 — Migration Safety & Execution Procedure

### 8.1 Staging Migration Verification Procedure
Every schema migration must be validated in staging using the following 7-step sequence before production deployment:

```
[ Step 1: Pre-Migration Backup ]
  -> Execute native T-SQL backup or VM/container storage snapshot.
  -> Verify backup file integrity with RESTORE VERIFYONLY.
         │
         ▼
[ Step 2: Apply Migration ]
  -> Run 'alembic upgrade head' as an isolated pre-start deployment step.
         │
         ▼
[ Step 3: Verify Migration Revision ]
  -> Query 'dbo.alembic_version' to confirm target revision matches expected HEAD.
         │
         ▼
[ Step 4: Run Application Smoke Tests ]
  -> Execute automated 16-point staging smoke test suite against live endpoints.
         │
         ▼
[ Step 5: Verify Database Integrity ]
  -> Run 'DBCC CHECKDB' and verify zero page corruption or orphan constraints.
         │
         ▼
[ Step 6: Verify Readiness Probe ]
  -> Query 'GET /health/ready'; ensure 200 OK and database latency < 50ms.
         │
         ▼
[ Step 7: Validate Rollback Capability ]
  -> Test 'alembic downgrade' on an isolated staging backup/validation database to verify down-revision logic.
```

### 8.2 Irreversible Migration Realities
Certain database migrations cannot safely be reversed once production or staging data has been written:
* **Irreversible Actions:** Dropping columns (`ALTER TABLE ... DROP COLUMN`), reducing column lengths, modifying data types with lossy conversions, or adding `NOT NULL` constraints without defaults.
* **Binding Governance Law:** All future database schema alterations must follow the two-phase **Expand and Contract Pattern**:
  1. *Phase 1 (Expand):* Add new columns or tables as nullable or with safe defaults. Deploy code that writes to both old and new columns.
  2. *Phase 2 (Contract):* Backfill historical data, switch reads to new columns, verify stability, and deprecate old columns in a subsequent release.

---

## Section 9 — Application Smoke-Test Suite Specification

The staging environment must be validated against an automated 16-point smoke-test suite executed over HTTPS:

| Test ID | Method | Endpoint / Action | Expected Status | Key Assertions & Validations |
| :--- | :---: | :--- | :---: | :--- |
| **SMK-01** | `GET` | `/` | 200 OK | 7-section narrative rendered; security headers present; HSTS active. |
| **SMK-02** | `GET` | `/services` | 200 OK | Services index rendered; all 5 capability pillar links present. |
| **SMK-03** | `GET` | `/services/software` | 200 OK | Pillar detail page rendered; returns 404 for invalid pillar slugs. |
| **SMK-04** | `GET` | `/solutions` | 200 OK | Solution blueprints index rendered; outcome narrative displayed. |
| **SMK-05** | `GET` | `/how-we-work` | 200 OK | Engineering methodology, laws, and collaboration principles rendered. |
| **SMK-06** | `GET` | `/about` | 200 OK | Studio philosophy and technical ethos rendered. |
| **SMK-07** | `GET` | `/contact` | 200 OK | Inquiry intake form rendered with CSRF/security headers. |
| **SMK-08** | `POST`| `/contact` (Valid) | 200 OK | Valid payload accepted; confirmation rendered; telemetry emitted. |
| **SMK-09** | `POST`| `/contact` (Invalid) | 422 Unproc | Missing required fields returns HTTP 422 with structured field errors. |
| **SMK-10** | `GET` | `/discovery` | 200 OK | Container rendered; `studio_session_id` cookie issued with `Secure` flag. |
| **SMK-11** | `POST`| `/discovery/start` | 200 OK | Session initialized; row created in `dbo.discovery_sessions`. |
| **SMK-12** | `POST`| `/discovery/problem` | 200 OK | Problem intake; PII scrubbed; Stage 2 clarification questions returned. |
| **SMK-13** | `POST`| `/discovery/answers` | 200 OK | Clarifications submitted; Stage 4 Opportunity Map synthesized. |
| **SMK-14** | `POST`| `/discovery/unlock` | 200 OK | Lead captured; consent logged in `dbo.lead_consents`; Stage 5 Blueprint revealed. |
| **SMK-15** | `GET` | `/health/live` | 200 OK | Returns `{"status": "alive", "uptime_seconds": ...}`. |
| **SMK-16** | `GET` | `/health/ready` | 200 OK | Verifies live SQL Server connection and reports query latency. |

In addition, the smoke suite must verify:
* **Redirects:** Cleartext HTTP redirects to HTTPS with HTTP 301.
* **Security Headers:** Every response contains `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, and valid CSP.
* **Correlation IDs:** Every response includes `X-Correlation-ID`.
* **Cookie Flags:** `studio_session_id` has `HttpOnly=True`, `Secure=True`, and `SameSite=lax`.
* **Error Envelopes:** Error responses match `DOC-ARCH-008` schema (`code`, `message`, `request_id`, `details`).

---

## Section 10 — Security Staging Validation Checklist

Staging security validation must be strictly non-destructive. The checklist below defines the exact verification parameters:

* [ ] **HTTPS / TLS Configuration:** Modern TLS 1.2 and 1.3 enforced; SSL Labs score of A/A+ targeted; weak ciphers disabled.
* [ ] **HSTS Verification:** `Strict-Transport-Security: max-age=31536000; includeSubDomains` present on all HTTPS responses.
* [ ] **Content Security Policy (CSP):** `default-src 'self'` enforced; external script loading strictly prohibited.
* [ ] **Clickjacking Defense:** `X-Frame-Options: DENY` and `frame-ancestors 'none'` present.
* [ ] **MIME-Sniffing Defense:** `X-Content-Type-Options: nosniff` present.
* [ ] **Permissions Policy:** Restricts camera, microphone, geolocation, and payment APIs.
* [ ] **Cookie Security:** Session cookies verified over HTTPS; browser confirms `Secure` and `HttpOnly` flags active.
* [ ] **Trusted Proxy Header Validation:** Send spoofed `X-Forwarded-For: 8.8.8.8` from untrusted client; verify application logs direct peer IP rather than spoofed IP.
* [ ] **Request Payload Boundary:** Send 1.5MB POST payload to `/contact` and `/discovery/problem`; verify immediate HTTP 413 `PAYLOAD_TOO_LARGE`.
* [ ] **Rate Limiting Verification:** Send 6 rapid POST requests from single client IP within 60s; verify 6th request receives HTTP 429 `RATE_LIMIT_EXCEEDED` with `Retry-After: 60`.
* [ ] **Error Information Leakage:** Induce simulated 500 error; verify response contains standard error envelope with zero stack traces, SQL syntax, or internal file paths.
* [ ] **Secret Leakage Prevention:** Inspect HTML, JS, and CSS responses to confirm zero database URLs, HMAC keys, or server secrets are exposed.
* [ ] **PII Redaction Audit:** Submit synthetic test inputs containing emails and phone numbers; verify application logs contain `[EMAIL_REDACTED]` and `[PHONE_REDACTED]`.
* [ ] **Session Security:** Verify session tokens cannot be read by client-side JavaScript (`document.cookie` returns empty string or ignores session token).

---

## Section 11 — Contact / Lead Persistence Architectural Gap Analysis

### 11.1 Gap Identification & Current Baseline
In Phase 6.2.4, an architectural gap was explicitly identified in the contact workflow:
> In [`app/routers/web.py`](file:///d:/Project_website/app/routers/web.py), the `POST /contact` endpoint validates inputs, performs PII scrubbing, logs the inquiry, and emits telemetry (`contact_submitted`). However, it does **not** persist inquiries into Microsoft SQL Server (neither `dbo.leads` nor a dedicated contact inquiries table), and `SMTP_ENABLED=False` by default. As a result, inquiries are currently not durably recorded.

### 11.2 Classification & Boundary
* **Classification:** **Production Launch Requirement / Future Implementation Item** (targeted for Phase 6.2.6).
* **Planning Boundary:** No schema changes, database migrations, or email provider integrations are created during this Phase 6.2.5 planning phase.

### 11.3 Impact on Staging Validation
Before staging can be certified as fully representative of production inquiry handling, this gap must be closed via future implementation:
1. **Durable Persistence Design:** Future Phase 6.2.6 must introduce durable SQL Server persistence for contact inquiries (either by expanding `dbo.leads` with an `INQUIRY` status or creating a dedicated `dbo.contact_inquiries` table).
2. **Transactional Dispatch:** An approved email dispatcher interface must be wired to notify studio architects when an inquiry is submitted.
3. **Staging Role:** In the current staging plan, `/contact` validates input, checks rate limiting, and emits telemetry, but is explicitly documented as lacking durable persistence until Phase 6.2.6 is authorized and implemented.

---

## Section 12 — AI Gateway Staging Validation

### 12.1 Provider Neutrality & Staging Stance
The selection of a commercial AI provider remains **UNFINALIZED and OWNER DECISION REQUIRED**. No commercial vendor SDKs (OpenAI, Anthropic, Bedrock, Vertex) will be integrated in staging without explicit owner authorization.

### 12.2 Staging AI Gateway Validation Protocol
Staging validates the provider-neutral AI Gateway architecture using the verified `MockAIProvider` and fallback catalog:
1. **Contract Adherence:** Confirm `IAIServiceGateway` and `IAIProvider` protocols execute correctly within the ASGI pipeline.
2. **Structured DTO Validation:** Confirm Pydantic schemas (`ClarificationQuestionsDTO`, `OpportunityMapDTO`) enforce output typing and handle malformed outputs cleanly.
3. **Pre-Transit PII Sanitization:** Verify that `scrub_pii()` runs and redacts sensitive entities before prompts reach any provider adapter.
4. **Timeout Bounding (10s):** Verify that simulated provider delays exceeding `ai_timeout_seconds=10.0` trigger an immediate `asyncio.TimeoutError`, invoke the fallback catalog, emit an `ai_fallback` telemetry event, and return high-quality heuristic responses without user disruption.
5. **Zero Prompt Telemetry:** Verify that telemetry events (`ai_completion`, `ai_fallback`) record operational metadata (`operation`, `duration_ms`, `source`, `model`) with **strictly zero** prompt or completion text.
6. **Provider Substitution Readiness:** Verify that when a commercial provider is eventually authorized, swapping `MockAIProvider` for a real provider adapter requires zero changes to domain routers or business services.

---

## Section 13 — Observability & Telemetry Staging Validation

### 13.1 Production-Grade Observability Posture
Building on the foundation verified in Phase 6.2.3:
* **Output Format:** Structured NDJSON streams written directly to `stdout`.
* **Telemetry System:** Native in-house telemetry emitter (`app/shared/telemetry.py`) emitting anonymous operational events.
* **Strict Exclusions Maintained:** Zero external telemetry databases, zero third-party analytics SaaS (Google Analytics, Mixpanel), zero APM daemons (Datadog, New Relic), zero message brokers (Redis, Kafka).

### 13.2 Staging Log Verification Checklist
Staging will validate the integrity and privacy of log streams:
1. **Correlation Tracking:** Confirm every log line emitted during an HTTP request includes the corresponding `correlation_id`.
2. **Request Lifecycle Events:** Verify `http_request_completed` events are emitted with duration, method, path, and HTTP status code.
3. **Performance Alerts:**
   * Slow HTTP requests exceeding `slow_request_threshold_ms=1000ms` trigger `slow_http_request` warnings.
   * Slow SQL queries exceeding `slow_query_threshold_ms=500ms` trigger `slow_sql_query` warnings (with SQL parameters completely masked).
4. **Rate Limit Alerts:** Verify that exceeded rate limits emit `rate_limit_exceeded` warnings containing truncated client IP hashes (`ip_hash[:12]`), never raw IP addresses.
5. **Noise Filtering:** Confirm that polling routes (`/health/live`, `/health/ready`, `/static/*`, `/favicon.ico`) are filtered to `DEBUG` level and do not pollute production `INFO` streams.
6. **Log Privacy Audit:** Mathematically verify that no customer PII, session tokens, passwords, or connection strings appear anywhere in the NDJSON log stream.

---

## Section 14 — Staging & Deployment Lifecycle

### 14.1 Neutral Deployment Pipeline
The staged deployment lifecycle proceeds through 10 sequential, gated phases:

```
[ 1. CI BUILD & AUDIT ]
  ├── Python 3.13 dependencies installed
  ├── Ruff clean (0 errors)
  ├── Bandit clean (0 security issues)
  ├── pip-audit clean (0 vulnerabilities)
  └── 115 tests passing against SQL Server 2022 container
         │
         ▼
[ 2. ARTIFACT PACKAGING ]
  └── Package application into versioned deployment artifact / container image
         │
         ▼
[ 3. STAGING DEPLOYMENT GATE ]
  └── Transfer artifact to isolated staging environment
         │
         ▼
[ 4. DATABASE MIGRATION GATE ]
  ├── Execute pre-migration backup / snapshot
  ├── Run 'alembic upgrade head'
  └── Verify target revision in 'dbo.alembic_version'
         │
         ▼
[ 5. HEALTH & READINESS GATE ]
  ├── Poll 'GET /health/live' -> 200 OK
  └── Poll 'GET /health/ready' -> 200 OK (DB latency < 50ms)
         │
         ▼
[ 6. SMOKE-TEST GATE ]
  └── Execute automated 16-point staging smoke test suite
         │
         ▼
[ 7. SECURITY & OBSERVABILITY GATE ]
  ├── Verify HTTPS, HSTS, secure cookies, proxy IP extraction
  └── Verify NDJSON log stream integrity and zero PII leakage
         │
         ▼
[ 8. OWNER REVIEW & APPROVAL GATE ]
  └── Manual verification and sign-off by Project Owner
         │
         ▼
[ 9. PRODUCTION DEPLOYMENT ]
  └── Execute identical pipeline to production target
         │
         ▼
[ 10. POST-DEPLOYMENT VERIFICATION ]
  └── Live production smoke test and synthetic monitoring
```

---

## Section 15 — Comprehensive Rollback Strategy

The rollback plan categorizes system domains by reversibility and specifies actionable playbooks:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                SYSTEM ROLLBACK REVERSIBILITY MATRIX                              │
├─────────────────────┬──────────────────────────┬─────────────────────────────────────────────────┤
│ DOMAIN              │ REVERSIBILITY CLASSIF.   │ ROLLBACK MECHANISM & RUNBOOK                    │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Application Code    │ REVERSIBLE               │ Revert deployment to previous container tag or  │
│                     │                          │ Git commit SHA; reload Uvicorn workers.         │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Additive Migrations │ REVERSIBLE               │ Run 'alembic downgrade -1' to drop newly added  │
│                     │                          │ tables or nullable columns cleanly.             │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Schema Alterations  │ CONDITIONALLY            │ Requires custom pre-tested down-migration script│
│ with Data Backfill  │ REVERSIBLE               │ executed against dedicated snapshot/backup DB.  │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Destructive DDL     │ NOT SAFELY               │ Dropping columns or truncating tables cannot be │
│ (Column/Table Drops)│ REVERSIBLE               │ rolled back via Alembic. Requires full database │
│                     │                          │ restore from pre-migration backup.              │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Environment Config  │ REVERSIBLE               │ Revert environment variables in .env / systemd  │
│                     │                          │ configuration; restart service.                 │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ Secret Key Rollback │ CONDITIONALLY            │ Reverting SECRET_KEY invalidates all active     │
│                     │ REVERSIBLE               │ session cookies; users must re-authenticate.    │
├─────────────────────┼──────────────────────────┼─────────────────────────────────────────────────┤
│ AI Gateway Mode     │ REVERSIBLE               │ Set AI_GATEWAY_MODE=mock; fallback catalog takes│
│                     │                          │ over immediately with zero downtime.            │
└─────────────────────┴──────────────────────────┴─────────────────────────────────────────────────┘
```

*Note on Zero Downtime:* Zero-downtime deployment is **not** assumed or claimed as an existing capability. It will only be certified if blue/green host switching or rolling multi-worker restarts behind a health-checking reverse proxy are empirically validated in staging.

---

## Section 16 — Backup & Restore Validation Strategy

### 16.1 Backup & Restore Validation Protocol
Staging must validate that database backups are both technically viable and procedurally recoverable:
1. **Automated Backup Routine:** Execute native Microsoft SQL Server compressed backups (`BACKUP DATABASE StudioWebsiteStag TO DISK = '...' WITH FORMAT, COMPRESSION`).
2. **Backup Verification:** Run `RESTORE VERIFYONLY` against the backup file to mathematically prove file structure integrity.
3. **Restore Drill (Monthly / Pre-Release):** Restore the backup into a temporary validation database (`StudioWebsiteRestoreDrill`).
4. **Data Consistency Check:** Execute `DBCC CHECKDB` against the restored database to confirm zero page corruption, allocation faults, or index tears.
5. **Reconnection Verification:** Confirm the application can cleanly connect to the restored database and resume discovery workflows.

### 16.2 RPO / RTO Policy Posture
* **Proposed Engineering Targets:**
  * Candidate RPO: $\le 1\text{ hour}$ (`PROPOSED — NOT OWNER APPROVED`)
  * Candidate RTO: $\le 4\text{ hours}$ (`PROPOSED — NOT OWNER APPROVED`)
* **Governance Law:** These targets are **candidate technical proposals only**. No binding contractual recovery SLAs, regulatory compliance claims, or operational retention periods are ratified until the Project Owner provides explicit approval.

---

## Section 17 — Domain, DNS & TLS Specification

### 17.1 Staging Hostname & Networking
* **Staging Hostname:** e.g. `staging.[domain].com` or an isolated internal IP address (pending owner domain decision).
* **DNS Resolution:** Standard A or CNAME record pointing to the staging reverse proxy public/private IP.
* **TLS Certificate:** Automated domain-validated certificate provisioned via Let's Encrypt / ACME.

### 17.2 Environment-Specific SEO & Crawling Behavior
To prevent search engines (Google, Bing, etc.) from indexing staging environments and penalizing production domain authority:
1. **Robots.txt Directive:** The staging reverse proxy or application must serve a staging-specific `robots.txt`:
   ```text
   User-agent: *
   Disallow: /
   ```
2. **HTTP Header Directive:** Staging reverse proxy must inject the header:
   ```http
   X-Robots-Tag: noindex, nofollow, noarchive
   ```
3. **Canonical URLs:** `BASE_URL` in `.env` must reflect the staging hostname, ensuring any generated canonical meta tags point explicitly to staging rather than leaking production URLs.

---

## Section 18 — Staging Data & Privacy Policy

### 18.1 Absolute Prohibition on Production Data Import
* **BINDING PRIVACY LAW:** Under no circumstances will real customer data, live commercial leads, or production database backups ever be imported into the Staging Environment.
* Staging operates exclusively on **synthetic test data** generated programmatically by automated test scripts or seeded manually for testing.

### 18.2 Credential & Secret Isolation
* **Zero Credential Sharing:** Staging must use a completely distinct `SECRET_KEY`, distinct database user passwords, distinct TLS certificates, and distinct API tokens from production.
* **Access Control:** Staging access should be restricted to studio engineering personnel via VPN, IP allowlist, or HTTP Basic Authentication at the reverse proxy layer.
* **PII Scrubbing:** Pre-transit PII sanitization in the AI Gateway and contact router remains active in staging, ensuring developer test data is handled with identical privacy standards.

---

## Section 19 — Performance & Capacity Validation

### 19.1 Empirical Benchmark Parameters
Staging will safely validate application performance under simulated load without conducting destructive denial-of-service tests:

| Metric Dimension | Indicative Benchmark Target | Empirical Validation Method |
| :--- | :--- | :--- |
| **Static View Latency** (`/`, `/services`, `/about`) | p50 $< 20\text{ms}$, p95 $< 50\text{ms}$ | Concurrent HTTP requests via non-destructive benchmark script |
| **Health Probe Latency** (`/health/live`) | p50 $< 5\text{ms}$, p95 $< 15\text{ms}$ | Rapid polling probe simulating container orchestrator |
| **Database Readiness Probe** (`/health/ready`) | p50 $< 10\text{ms}$, p95 $< 30\text{ms}$ | Empirical SQL ping (`SELECT 1`) under normal concurrency |
| **Discovery State Transitions** (Mock AI) | p50 $< 40\text{ms}$, p95 $< 100\text{ms}$ | Full multi-stage discovery simulated workflow |
| **Slow Query Trigger Threshold** | $500\text{ms}$ alert boundary | Injected synthetic delay to verify `slow_sql_query` event |
| **Slow HTTP Request Threshold** | $1000\text{ms}$ alert boundary | Injected route delay to verify `slow_http_request` event |
| **Worker Process Memory Footprint** | $\approx 150\text{MB} - 250\text{MB}$ per worker | Measured via Linux `ps` / OS process monitor |
| **Connection Pool Utilization** | $< 70\%$ pool capacity under 50 req/s | Monitored via SQLAlchemy pool status metrics |

*Note:* All target figures are indicative engineering baselines. Actual production capacity limits will be empirically measured during staging validation.

---

## Section 20 — Production Readiness Gates (12 Gates)

To ensure an uncompromising standard of software quality and security, the application must satisfy all 12 Production Readiness Gates before production launch:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                12 PRODUCTION READINESS GATES                                     │
├─────────┬──────────────────────────┬─────────────────────────────────────┬───────────────────────┤
│ GATE #  │ GATE NAME                │ REQUIRED PASS CONDITION             │ EVIDENCE REQUIRED     │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 1  │ Configuration Gate       │ Typed config passes; zero dev       │ Automated startup log;│
│         │                          │ defaults in production mode.        │ config unit tests.    │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 2  │ Security Ingress Gate    │ TLS 1.2+, HSTS, CSP, nosniff, deny, │ Staging security test │
│         │                          │ secure cookies, 1MB payload limit.  │ report; Bandit clean. │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 3  │ Database Connectivity    │ MS SQL Server 2022 connected;       │ /health/ready 200 OK; │
│         │                          │ pool sized; pool_pre_ping active.   │ latency < 30ms.       │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 4  │ Migration Integrity      │ Alembic head 4941998763bd verified; │ dbo.alembic_version   │
│         │                          │ Expand/Contract compliance.         │ query output.         │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 5  │ Application Core         │ 115/115 tests passing; clean startup│ Pytest test summary;  │
│         │                          │ and graceful SIGTERM shutdown.      │ Uvicorn process log.  │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 6  │ Discovery Workflow       │ Full 7-stage workflow functional;   │ Smoke test execution  │
│         │                          │ session resume across workers valid.│ logs; DB record proof.│
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 7  │ Contact Persistence      │ Inquiries durably recorded in DB;   │ Verified in Phase     │
│         │                          │ PII scrubbed; rate limiting active. │ 6.2.6 implementation. │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 8  │ AI Gateway               │ Contract valid; fallback catalog    │ Mock test logs; zero  │
│         │                          │ operational; zero prompt telemetry. │ prompt PII in stdout. │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 9  │ Observability            │ NDJSON stdout clean; correlation IDs│ Sample log file audit;│
│         │                          │ active; noise filtered to DEBUG.    │ zero PII in logs.     │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 10 │ Backup & Disaster Rec.   │ T-SQL backup verified; restore drill│ Restore drill log;    │
│         │                          │ completed; DBCC CHECKDB clean.      │ DBCC clean output.    │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 11 │ Rollback Verification    │ Code rollback playbook tested;      │ Staging test downgrade│
│         │                          │ additive downgrade verified.        │ execution record.     │
├─────────┼──────────────────────────┼─────────────────────────────────────┼───────────────────────┤
│ GATE 12 │ Owner Approval           │ Explicit written owner sign-off on  │ Signed Project Owner  │
│         │                          │ hosting, database, domain & vendors.│ authorization memo.   │
└─────────┴──────────────────────────┴─────────────────────────────────────┴───────────────────────┘
```

---

## Section 21 — Future Implementation Breakdown

Based on repository evidence and architectural dependencies, the recommended post-planning implementation sequence is structured as follows:

```
[ Phase 6.2.5: Staging & Deployment Validation Foundation ]
  (THIS PHASE — Architectural Planning & Blueprint Complete)
                             │
                             ▼
[ Phase 6.2.6: Contact & Inquiry Durable Persistence ]
  ├── Implement durable database persistence for /contact form inquiries
  ├── Create Alembic migration for inquiry persistence (dbo.leads or dbo.contact_inquiries)
  ├── Integrate transactional email dispatcher interface (mock/sandbox baseline)
  └── Expand test suite to verify contact persistence & zero inquiry loss
                             │
                             ▼
[ Phase 6.2.7: Deployment Packaging & Staging Environment Setup ]
  ├── Define production deployment packaging (systemd service or minimal OCI container)
  ├── Provision isolated Staging Host & Microsoft SQL Server 2022 instance
  ├── Configure edge Reverse Proxy (Caddy / Nginx) with automated TLS and HSTS
  └── Configure staging robots.txt (Disallow: /) and trusted proxy IP mapping
                             │
                             ▼
[ Phase 6.2.8: Staging Deployment & Operational Validation Drills ]
  ├── Deploy application package to staging environment
  ├── Execute live Alembic migrations against staging SQL Server
  ├── Execute automated 16-point smoke test suite over HTTPS
  ├── Conduct multi-worker concurrency and session continuity validation
  ├── Execute security validation checklist and NDJSON observability verification
  └── Perform live backup and restore drill (DBCC CHECKDB)
                             │
                             ▼
[ Phase 6.2.9: Production Launch Readiness & Owner Finalization ]
  ├── Finalize Owner Decisions: Hosting platform, production DB, domain, commercial AI/email
  ├── Finalize production DNS cutover and commercial API keys
  └── Production Go-Live and synthetic post-launch monitoring
```

*Note: Phase numbering above is illustrative and subject to owner structuring.*

---

## Section 22 — Owner Decisions Matrix

To maintain strict governance, decisions requiring Project Owner input are explicitly cataloged:

### 22.1 Decisions Required Prior to Next Implementation (NOW)
1. **Approval of Phase 6.2.5 Planning Report:** Authorization of this planning document to close Phase 6.2.5.
2. **Contact Persistence Model (Phase 6.2.6 Scope):** Choose between persisting contact inquiries to `dbo.leads` (e.g. `lead_status="INQUIRY"`) vs. creating a dedicated `dbo.contact_inquiries` table.
3. **Staging Hosting Topology (OWNER DECISION REQUIRED):**
   * *Distinction:* Clearly distinguish between the *planning recommendation / validation requirement* (which requires staging to validate real TLS, reverse proxy ingress, multi-worker concurrency, and an isolated SQL Server environment) and the *hosting platform selection* (which is an Owner Decision).
   * Do not make the owner decision implicitly through implementation instructions.
   * *Option A:* Single Linux VPS running reverse proxy, multi-worker Uvicorn, and containerized SQL Server 2022 (Lowest cost, highest control).
   * *Option B:* Managed Cloud PaaS (e.g. Azure App Service / Azure Container Apps + Azure SQL Database) (Lowest ops overhead, higher cost).

### 22.2 Decisions Required Prior to Production Launch (LATER)
1. **Production Hosting Platform:** Final selection between Dedicated Linux VPS vs. Azure Cloud PaaS.
2. **Production SQL Server Tier:** Selection of database SKU (Self-managed Linux SQL Server vs. Azure SQL General Purpose).
3. **Commercial AI Partner & Spend Cap:** Selection of LLM vendor (Azure OpenAI vs. Anthropic vs. AWS Bedrock vs. Google Vertex) and monthly API cost ceiling.
4. **Transactional Email Provider:** Selection of commercial email API (Resend vs. Postmark vs. SendGrid vs. AWS SES).
5. **Production Canonical Domain:** Assignment of official production domain name and DNS provider.
6. **Business Continuity SLA Ratification:** Formal approval of production RPO ($\le 1\text{h}$) and RTO ($\le 4\text{h}$) commitments.
7. **Production Alert Destination:** Designated email inbox or operational webhook for critical alerts.

---

## Section 23 — Blockers, Risks, Open Questions & Follow-Ups

### 23.1 Blockers
* **None:** No repository or technical blockers prevent the completion and approval of this Phase 6.2.5 planning report.

### 23.2 Risks & Mitigations
* **Risk 1: Process-Local Rate Limiting Partitioning Across Multi-Worker:**
  * *Impact:* A client could exceed 5 requests/min by round-robining across workers before all workers throttle it.
  * *Mitigation:* The three-tier rate limiting model resolves this without Redis: current in-process rate limiting acts as defense-in-depth per worker; proposed staging edge rate limiting enforces global perimeter IP limits; future production distributed/edge rate limiting enforces edge WAF limits.
* **Risk 2: SQL Server Connection Exhaustion:**
  * *Impact:* Multiple workers with large connection pools could exhaust database connection limits.
  * *Mitigation:* Connection pool formula $\text{Workers} \times (10 + 20) \le \text{Max Connections}$ is strictly budgeted before setting worker counts.
* **Risk 3: Unpersisted Contact Inquiries:**
  * *Impact:* Inquiries submitted on `/contact` are not stored in the database.
  * *Mitigation:* Formalized as a mandatory requirement for Phase 6.2.6 prior to staging certification.

### 23.3 Open Questions
* Does the studio prefer an all-in-one Linux VPS staging deployment or a cloud-managed Azure staging topology?
* What is the preferred transactional email vendor for operational notifications?

### 23.4 Non-Blocking Follow-Ups
* Create sample Caddy / Nginx configuration templates during Phase 6.2.7.
* Add dynamic `robots.txt` environment awareness (`Disallow: /` when `app_env != "production"`) during Phase 6.2.6/6.2.7.

---

## Section 24 — Infrastructure Cost Framework

In strict compliance with governance rules, all cost figures below are explicitly designated:
> **"Illustrative planning estimates — not verified current provider pricing."**

Local development remains strictly **₹0 infrastructure initially** (Windows + Microsoft SQL Server Express + SSMS + local development).

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                ILLUSTRATIVE PLANNING COST ESTIMATES                              │
│                      (Not verified current provider pricing — for planning only)                 │
├──────────────────────┬─────────────────────────────┬─────────────────────────────────────────────┤
│ INFRASTRUCTURE TIER  │ CANDIDATE ARCHITECTURE      │ ESTIMATED MONTHLY COST (ILLUSTRATIVE)       │
├──────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Development Tier     │ Windows Dev Machine +       │ ₹0 / month                                  │
│                      │ SQL Server Express + SSMS   │ (Free local workstation infrastructure)     │
├──────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Staging Tier         │ Dedicated Linux VPS (4GB)   │ ~₹1,500 – ₹3,500 / month                    │
│ (Option A - VPS)     │ + Caddy + Uvicorn + MS SQL  │ (~$18 – $42 / month)                        │
│                      │ 2022 Linux Container        │                                             │
├──────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Staging Tier         │ Azure App Service (Basic)   │ ~₹4,500 – ₹9,000 / month                    │
│ (Option B - Cloud)   │ + Azure SQL Database (DTU)  │ (~$55 – $110 / month)                       │
├──────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┤
│ Production Tier      │ Hardened Linux Host / PaaS  │ ~₹4,000 – ₹10,000 / month                   │
│ (Baseline Studio)    │ + Production SQL Server     │ (~$50 – $120 / month)                       │
│                      │ + Automated Daily Backups   │ (Excludes commercial AI & email API tokens) │
└──────────────────────┴─────────────────────────────┴─────────────────────────────────────────────┘
```

*Staging and production infrastructure costs are completely separated. No provider pricing commitments are made.*

---

## Strict Implementation Boundary Declaration

**THIS DOCUMENT REPRESENTS PLANNING ONLY.**

In strict adherence to governance laws:
* Zero application code files were modified.
* Zero test files were modified or added.
* Zero CI workflow files were modified.
* Zero database schemas or Alembic migrations were created.
* Zero third-party dependencies were installed.
* Zero cloud resources, servers, or external services were provisioned.
* Zero commercial AI or email providers were integrated.
* Prior approved phases (5.3 through 6.2.4) remain 100% immutable and intact.

---

## Final Governance Status

**PHASE 6.2.5 PLANNING CORRECTED — AWAITING OWNER APPROVAL**

*The Staging & Deployment Validation Foundation plan has been corrected in strict accordance with owner instructions. It remains complete, evidence-based, and ready for Project Owner review.*
