# Phase 6.2.4 — Production Readiness & Deployment Foundation Plan

**Document ID:** `DOC-REP-6.2.4-PLAN`  
**Phase:** Phase 6.2.4 (Production Readiness & Deployment Foundation)  
**Status:** CANONICAL PLANNING REPORT — PLANNING ONLY — REVISED & CORRECTED — AWAITING OWNER APPROVAL  
**Date:** 2026-09-18  
**Architecture Preserved:** Python 3.13 · FastAPI · Uvicorn · Jinja2 · HTMX · Alpine.js · SQLAlchemy 2.x · Alembic · Microsoft SQL Server 2022 · pyodbc · Modular Monolith  
**Authoritative Scope:** Planning and specification only. Zero application code modified, zero migrations created, zero dependencies installed, zero cloud infrastructure provisioned, zero irreversible vendor lock-in decisions made.

---

## Executive Summary & Purpose

This document establishes the canonical, evidence-based **Production Readiness & Deployment Foundation Plan** for `[STUDIO_NAME]`. 

With the successful completion and independent owner verification of **Phase 6.2.3** (observability, anonymous application telemetry, and 105/105 tests passing against live Microsoft SQL Server 2022 containers in GitHub Actions CI), the application has attained a verified development and CI baseline. 

The objective of **Phase 6.2.4** is strictly **PLANNING ONLY**: to evaluate the gap between the current verified baseline and production readiness, establish a provider-neutral deployment architecture, audit security, database, secrets, observability, AI gateway, email, and scaling characteristics, provide decision frameworks for external services, and formulate a structured, risk-mitigated path toward staging and production launch.

---

## Repository & Documentation Audit

### 1. Current Git & Repository State
- **Active Branch:** `main`
- **Working Tree:** Clean (verified via `git status`)
- **Remote Tracking:** Up to date with `origin/main` (`https://github.com/dev806/website.git`)
- **Latest Commits:**
  - `b17e196`: `docs: finalize Phase 6.2.3 implementation report with live CI verification`
  - `9bc6f56`: `Phase 6.2.3: Isolated logging fixture and unversioned CI test step`
  - `3cc2ad2`: `Preserve test log capture handlers in configure_logging`
- **Active Test Count:** 105 collected tests (98 main application tests + 7 Sprint 0 live regression tests).
- **Alembic Migration Head:** `4941998763bd` (`initial_mvp_foundation.py`).
- **Static Quality & Security Audits:** Ruff clean (0 lint violations), Bandit clean (0 security issues), pip-audit clean (0 vulnerable dependencies).

### 2. Documentation Audit — Authoritative vs. Stale / Drifted

An exhaustive audit of the `/docs` hierarchy reveals that documentation falls into two distinct categories:

| Document | Classification | Current State / Drift Identified |
| :--- | :---: | :--- |
| [`docs/00-project/PHASE-6.2.3-IMPLEMENTATION-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.2.3-IMPLEMENTATION-REPORT.md) | **Authoritative** | Canonical record of Phase 6.2.3 (NDJSON stdout, telemetry emitter, slow query hooks, test isolation). |
| [`docs/00-project/PHASE-6.2.2-IMPLEMENTATION-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.2.2-IMPLEMENTATION-REPORT.md) | **Authoritative** | Canonical record of CI pipeline against official Microsoft SQL Server 2022 Linux container. |
| [`docs/00-project/PHASE-6.2.1-IMPLEMENTATION-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.2.1-IMPLEMENTATION-REPORT.md) | **Authoritative** | Canonical record of T-SQL schema, DDL definitions, pyodbc connection pool, and Alembic head. |
| [`docs/00-project/PHASE-6.1-FINAL-AUDIT-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.1-FINAL-AUDIT-REPORT.md) | **Authoritative** | Canonical record of security middleware, rate limiting, and PII scrubbing. |
| [`docs/00-project/PROJECT_CONSTRAINTS.md`](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md) | **Authoritative** | Governing constraints: `CST-CNF-007` (Modular Monolith) and `CST-CNF-008` (₹0 Local Dev Infra). |
| [`docs/00-project/DECISION_LOG.md`](file:///d:/Project_website/docs/00-project/DECISION_LOG.md) | **Authoritative** | Immutable records: `BD-001` (MSSQL), `BD-015` (Python-first), `BD-009` (HTMX/Alpine). |
| [`docs/05-architecture/01-SYSTEM-ARCHITECTURE.md`](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | **Stale / Drifted** | Written in Phase 4; specifies Python 3.12+ (now strictly Python 3.13), references LiteLLM (now provider-neutral `IAIProvider` protocol with Mock), and lists BackgroundTasks for email (currently disabled). |
| [`docs/17-devops/01-DEVOPS-SPECIFICATION.md`](file:///d:/Project_website/docs/17-devops/01-DEVOPS-SPECIFICATION.md) | **Stale / Drifted** | Early draft containing unverified pricing numbers and unapproved RPO/RTO targets; CI YAML in this doc is superseded by `.github/workflows/ci.yml`. |
| [`docs/05-architecture/22-DEVOPS-AND-DEPLOYMENT.md`](file:///d:/Project_website/docs/05-architecture/22-DEVOPS-AND-DEPLOYMENT.md) | **Stale / Drifted** | Early conceptual deployment diagram; does not reflect containerized CI verification or current security middleware order. |
| [`docs/05-architecture/23-BACKUP-DISASTER-RECOVERY.md`](file:///d:/Project_website/docs/05-architecture/23-BACKUP-DISASTER-RECOVERY.md) | **Stale / Drifted** | Contains premature RPO ($\le 1$h) and RTO ($\le 4$h) targets [PROPOSED — NOT OWNER APPROVED] not yet reviewed or funded by the owner. |
| [`docs/05-architecture/10-AI-ARCHITECTURE.md`](file:///d:/Project_website/docs/05-architecture/10-AI-ARCHITECTURE.md) | **Stale / Drifted** | Assumed direct LiteLLM deployment; current architecture is abstracted through `app/ai_gateway/interface.py`. |

---

## SECTION 1 — Current Production Readiness Baseline

A factual inventory of all application components, evaluated strictly against current repository evidence:

| Component / Area | Status | Repository Evidence | Technical Analysis & Gap Description |
| :--- | :---: | :--- | :--- |
| **Application Runtime** | **PARTIALLY READY** | [`app/main.py:301`](file:///d:/Project_website/app/main.py#L301), [`requirements.txt:58`](file:///d:/Project_website/requirements.txt#L58) | FastAPI 0.141 + Uvicorn 0.52 running on Python 3.13. Single-process local dev verified. Multi-worker production process manager (Gunicorn/Uvicorn worker supervisor) not yet configured. |
| **Configuration** | **READY** | [`app/config.py:26-86`](file:///d:/Project_website/app/config.py#L26-L86) | Typed Pydantic Settings v2 with environment resolution, default validations, and `SecretStr` masking for credentials. |
| **Environment Management** | **READY** | [`app/config.py:31-33`](file:///d:/Project_website/app/config.py#L31-L33) | `app_env` enum supporting `development`, `testing`, `staging`, `production`. Local `.env` ignored in git. |
| **Secrets Management** | **PARTIALLY READY** | [`app/config.py:38-48`](file:///d:/Project_website/app/config.py#L38-L48), [`.env.example`](file:///d:/Project_website/.env.example) | Sensitive fields wrapped in `SecretStr`. However, secrets currently load only from env vars / `.env`. Production secret injection (Azure Key Vault, AWS Secrets Manager, etc.) is unconfigured. |
| **Database Engine** | **READY** | [`app/database/connection.py:57-72`](file:///d:/Project_website/app/database/connection.py#L57-L72) | SQLAlchemy 2.0.52 with pyodbc 5.3.0 and ODBC Driver 18 for SQL Server. Verified live against local SQL Server Express and remote Linux container in CI. |
| **Database Migrations** | **READY** | [`alembic.ini`](file:///d:/Project_website/alembic.ini), [`migrations/versions/4941998763bd_initial_mvp_foundation.py`](file:///d:/Project_website/migrations/versions/4941998763bd_initial_mvp_foundation.py) | Alembic lifecycle verified. Single head `4941998763bd`. Migration upgrade, downgrade, and re-upgrade tested cleanly in CI test suite. |
| **Connection Pooling** | **READY** | [`app/database/connection.py:63-70`](file:///d:/Project_website/app/database/connection.py#L63-L70) | Engine pool configured: `pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True`. `dispose_engine()` executes on shutdown. |
| **Health Checks (Liveness)** | **READY** | [`app/routers/health.py:22-33`](file:///d:/Project_website/app/routers/health.py#L22-L33) | `GET /health/live` returns HTTP 200 with process uptime in seconds. Verified by automated tests. |
| **Readiness Checks** | **READY** | [`app/routers/health.py:35-73`](file:///d:/Project_website/app/routers/health.py#L35-L73) | `GET /health/ready` executes live `SELECT 1` ping against SQL Server; returns 200 OK with query latency or 503 Service Unavailable on failure. |
| **Logging Pipeline** | **READY** | [`app/shared/logging.py:36-84`](file:///d:/Project_website/app/shared/logging.py#L36-L84) | Single-line structured NDJSON in production (`JSONLogFormatter`). `SensitiveFilter` scrubs bearer tokens, API keys, and email addresses from logs. |
| **Application Telemetry** | **READY** | [`app/shared/telemetry.py:46-95`](file:///d:/Project_website/app/shared/telemetry.py#L46-L95) | In-house emitter with zero third-party dependencies. 7 canonical product funnel events + operational events. Dropping of PII payload keys enforced. |
| **Security Headers** | **PARTIALLY READY** | [`app/main.py:150-168`](file:///d:/Project_website/app/main.py#L150-L168) | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`, HSTS on prod/https. CSP currently permits `'unsafe-inline'` for inline scripts/styles (requires future tightening). |
| **Rate Limiting** | **PARTIALLY READY** | [`app/main.py:30-72`](file:///d:/Project_website/app/main.py#L30-L72) | Native sliding-window rate limiter (5 req/60s on 7 POST routes). Process-local in-memory store; will partition across multiple worker processes unless handled at reverse proxy. `_get_client_ip` trusts `X-Forwarded-For` without trusted proxy validation. |
| **Sessions & Cookies** | **PARTIALLY READY** | [`app/modules/discovery/session_manager.py:29-52`](file:///d:/Project_website/app/modules/discovery/session_manager.py#L29-L52), [`app/routers/discovery_views.py:56-65`](file:///d:/Project_website/app/routers/discovery_views.py#L56-L65) | HMAC-SHA256 signed `studio_session_id` cookie. SHA-256 hash stored in DB (raw token never stored). `session_secure_cookie` defaults to `False` in dev; must be set to `True` for HTTPS production. Notice: `app/modules/discovery/router.py:83` reflects raw token in `X-Session-Token` header for tests (must be suppressed in prod). |
| **Error Handling** | **READY** | [`app/main.py:230-284`](file:///d:/Project_website/app/main.py#L230-L284), [`app/shared/exceptions.py`](file:///d:/Project_website/app/shared/exceptions.py) | Uniform error envelope (`format_error_response`) with correlation ID. Internal 500 errors suppress tracebacks to clients and log securely. |
| **AI Gateway Core** | **PARTIALLY READY** | [`app/ai_gateway/gateway.py:26-202`](file:///d:/Project_website/app/ai_gateway/gateway.py#L26-L202) | Provider-neutral interface (`IAIProvider`), PII scrubbing before transit, timeout bounding (`ai_timeout_seconds`), Pydantic DTO validation, and deterministic fallback catalog. Commercial LLM adapter is currently missing (operates on `MockAIProvider`). |
| **AI Provider Configuration** | **REQUIRES DECISION** | [`app/config.py:54-59`](file:///d:/Project_website/app/config.py#L54-L59) | No commercial provider (OpenAI, Azure OpenAI, Anthropic, Bedrock, Vertex) selected. No API keys, usage limits, or spend quotas configured. |
| **Email / Contact Handling** | **PARTIALLY READY** | [`app/routers/web.py:240-307`](file:///d:/Project_website/app/routers/web.py#L240-L307) | `/contact` validates input, scrubs PII, and emits `contact_submitted` telemetry. **CRITICAL GAP:** Inquiries are NOT persisted to SQL Server (`dbo.leads` is only populated via Discovery Stage 5 unlock). `SMTP_ENABLED=False`; inquiries may currently be unrecorded. **Classified as: Production launch requirement / future implementation item.** |
| **Static Assets** | **PARTIALLY READY** | [`static/`](file:///d:/Project_website/static/), [`templates/layouts/base.html:17-22`](file:///d:/Project_website/templates/layouts/base.html#L17-L22) | 100% locally vendored (`main.css`, `alpine.min.js`, `htmx.min.js`). Zero external CDN dependencies. However, `/static` route lacks explicit production `Cache-Control` headers (should be offloaded to reverse proxy). |
| **SEO Architecture** | **READY** | [`templates/`](file:///d:/Project_website/templates/), [`app/routers/web.py:348-408`](file:///d:/Project_website/app/routers/web.py#L348-L408) | Semantic HTML5, canonical links, Open Graph metadata, dynamic XML sitemap (`/sitemap.xml`), and robots.txt (`/robots.txt`). |
| **Accessibility** | **READY** | [`templates/layouts/base.html:46-60`](file:///d:/Project_website/templates/layouts/base.html#L46-L60) | Skip-to-main-content link, WCAG 2.1 AA landmarks, ARIA expanded attributes, keyboard navigation for mobile/dropdown menus. |
| **CI Quality Pipeline** | **READY** | [`.github/workflows/ci.yml`](file:///d:/Project_website/.github/workflows/ci.yml) | GitHub Actions running official SQL Server 2022 Linux container. Executes full test suite, Sprint 0 tests, Ruff, Bandit, and pip-audit. |
| **Automated Test Suite** | **READY** | [`tests/`](file:///d:/Project_website/tests/), [`spikes/test_sprint0_suite.py`](file:///d:/Project_website/spikes/test_sprint0_suite.py) | 105 tests passing deterministically. Comprehensive coverage of FSM, database lifecycle, security, observability, and public routes. |
| **Dependency Management** | **PARTIALLY READY** | [`requirements.txt`](file:///d:/Project_website/requirements.txt) | Pinned dependencies. However, runtime, test, and audit tools are mixed in a single file. Separate `requirements/base.txt` and `requirements/dev.txt` or a locked deployment file are needed. |
| **Observability Pipeline** | **PARTIALLY READY** | [`app/shared/logging.py`](file:///d:/Project_website/app/shared/logging.py), [`scripts/inspect_telemetry.py`](file:///d:/Project_website/scripts/inspect_telemetry.py) | Structured NDJSON emitted to stdout. Offline developer CLI exists. Production log forwarder (FluentBit / Vector / Azure Monitor) not yet attached. |
| **Backup & Recovery** | **MISSING** | None in repository | No automated SQL Server backup scripts, snapshot policies, or verified restore runbooks exist in the repository. |
| **Deployment Mechanism** | **MISSING** | None in repository | No production Dockerfile, Compose file, Helm chart, or container app definition exists in the repository. |
| **Rollback Mechanism** | **MISSING** | None in repository | No automated rollback trigger (e.g. on `/health/ready` failure post-deployment) exists. |
| **Production Monitoring** | **MISSING** | None in repository | No cloud alerts, uptime pingers, or threshold monitors are configured. |
| **Incident Response** | **MISSING** | None in repository | No operational runbooks, on-call matrices, or incident severity guidelines exist. |
| **Documentation Posture** | **READY** | [`docs/`](file:///d:/Project_website/docs/) | Detailed project records, architectural decision logs, and verified implementation reports. |
| **Privacy & Security** | **PARTIALLY READY** | [`app/shared/security.py`](file:///d:/Project_website/app/shared/security.py) | PII scrubbing and token hashing active. Production HTTPS enforcement, trusted proxy validation, and contact inquiry retention policies require implementation. |

---

## SECTION 2 — Production Deployment Architecture

### 1. Logical Request Flow
The production architecture maintains the Python-first modular monolith principles (`BD-015`) while establishing a secure, provider-neutral boundary:

```
[ Internet Client (Browser) ]
              │
              │ HTTPS (TLS 1.3 / Port 443)
              ▼
┌─────────────────────────────────────────────────────────┐
│ Edge / Ingress Tier (Cloudflare / Azure Front Door / CDN)│
│  - DDoS Protection & Edge Caching                       │
│  - TLS Termination & Automated Certificate Management   │
└─────────────────────────────┬───────────────────────────┘
                              │ HTTP/2 or HTTP/1.1 (Internal Mesh)
                              ▼
┌─────────────────────────────────────────────────────────┐
│ Reverse Proxy Tier (Caddy / Nginx / Managed Ingress)    │
│  - Enforce trusted proxy IP headers                     │
│  - Strip malicious X-Forwarded-For spoofing             │
│  - Offload & cache static assets (/static/*)            │
│  - Ingress rate limiting (IP-based)                     │
│  - Route application traffic to ASGI upstream           │
└─────────────────────────────┬───────────────────────────┘
                              │ HTTP (Port 8000 / Unix Socket)
                              ▼
┌─────────────────────────────────────────────────────────┐
│ Application Container / Process Tier (FastAPI + Uvicorn)│
│  - Worker Supervisor: Gunicorn / Uvicorn (N workers)    │
│  - Security Middleware & Correlation ID Injection       │
│  - Domain Modules (Web, Discovery, Leads, Health)       │
│  - In-Process Telemetry & Slow Query Detection          │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
               │ TDS over TLS (Port 1433) │ HTTPS Outbound (TLS)
               ▼                          ▼
┌──────────────────────────────┐ ┌────────────────────────────────┐
│ Database Tier                │ │ External Services Tier         │
│ Microsoft SQL Server         │ │ 1. AI Provider (LLM API)       │
│ - Azure SQL / Container / VM │ │    (Bounded timeout, fallback) │
│ - Encrypted in transit       │ │ 2. Transactional Email API     │
│ - Dedicated Least-Priv User  │ │    (When approved by owner)    │
└──────────────────────────────┘ └────────────────────────────────┘
               │                                  ▲
               ▼ stdout (NDJSON)                  │
┌──────────────────────────────────────────────┐  │
│ Observability Log Router (Vector / FluentBit)├──┘
│  - Ship logs to Log Analytics / CloudWatch   │
│  - Alert on 5xx, Slow Queries, AI Fallbacks  │
└──────────────────────────────────────────────┘
```

### 2. Technical Characteristics: Verified vs. Proposed

| Architectural Element | Currently Verified Baseline | Proposed for Production |
| :--- | :--- | :--- |
| **Process Model** | Single Uvicorn process (`uvicorn app.main:app --reload`) | Gunicorn supervisor with Uvicorn worker class (`uvicorn.workers.UvicornWorker`) or managed container cluster. |
| **Worker Count** | 1 process | Budgeted based on CPU: $W = (2 \times \text{vCPU}) + 1$ (e.g., 2–4 workers for initial deployment). |
| **Concurrency** | Asyncio event loop with Starlette threadpool for synchronous `pyodbc` database calls. | Maintained: Starlette threadpool offloads blocking DB calls; worker concurrency bounded by DB connection pool. |
| **Graceful Shutdown** | `lifespan` context manager handles `dispose_engine()` on SIGINT/SIGTERM. | Maintained: Container orchestrator sends SIGTERM, waits 30s for in-flight HTTP requests to complete, then disposes DB connections. |
| **Startup / Readiness** | Lazy engine connection; `/health/ready` validates connectivity via `SELECT 1`. | Container orchestrator startup probe queries `/health/live`; readiness probe queries `/health/ready` before routing traffic. |
| **Static Asset Handling** | FastAPI `StaticFiles` mounted at `/static` reading local disk. | Reverse proxy (Caddy/Nginx) or CDN serves `/static` directly with immutable cache headers (`Cache-Control: public, max-age=31536000`). |
| **HTTPS Termination** | Handled manually or disabled in local development. | Terminated at Reverse Proxy / Edge with automated Let's Encrypt or Cloud-Managed TLS certificates. |
| **Environment Separation** | `.env` file on local developer workstation; CI environment variables. | Immutable runtime containers with environment variables injected by container platform / secret store. |
| **Secret Injection** | Plaintext in local `.env` and GitHub Actions secrets. | Cloud Key Vault / Secret Store (e.g. Azure Key Vault, AWS Secrets Manager) injected at container startup. |
| **Database Connectivity** | Local named instance `.\SQLEXPRESS` (Windows) or container `127.0.0.1:1433` (CI). | Dedicated connection string with `Encrypt=yes;TrustServerCertificate=no;` connecting to hardened SQL Server. |
| **Outbound Egress** | None (Mock AI provider, SMTP disabled). | HTTPS egress to approved commercial AI provider and transactional email provider with strict request timeouts. |
| **Log Collection** | stdout (console text or NDJSON) + `scripts/inspect_telemetry.py`. | stdout captured by container runtime driver and shipped to central monitoring repository. |

---

## SECTION 3 — Hosting Options Neutral Comparison

To preserve architectural neutrality and the governing constraint (`CST-CNF-008`: ₹0 dev infrastructure), production hosting is evaluated objectively without declaring an arbitrary "best":

| Criteria | Option A: Azure App Service (Linux) | Option B: Azure Container Apps (ACA) | Option C: Linux VPS (Hetzner / DO / Azure VM) | Option D: Managed PaaS (AWS ECS / Render / Railway) |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI Compatibility** | Native (custom Docker container or Linux Python 3.13 blessed runtime). | Native (Docker container). | Native (Docker + systemd or Docker Compose). | Native (Dockerfile or buildpack). |
| **SQL Server Connectivity** | Native high-speed backbone to Azure SQL Database or private VNet. | Native high-speed backbone to Azure SQL Database or private VNet. | Connects over TLS to managed SQL Server or local containerized SQL Server. | Connects over TLS to managed SQL Server (AWS RDS MSSQL or Azure SQL). |
| **Deployment Complexity** | Low (Zip deploy or container push to ACR). | Low–Medium (OCI container image deployed via GitHub Actions). | Medium (Requires server provisioning, SSH keys, firewall, Docker setup). | Low–Medium (Git push or container registry integration). |
| **Operational Burden** | Low (Fully managed OS, patching, and scaling). | Low (Serverless container runtime managed by Azure). | High (Self-managed OS updates, security hardening, backups). | Low–Medium (Managed infrastructure; provider handles OS). |
| **Scaling Model** | Vertical (B1, P1v3) and horizontal scale-out. | Event-driven / HTTP-driven autoscaling down to 0 or min-replicas. | Fixed capacity (vertical resize requires downtime). | Horizontal autoscaling based on CPU/Memory or HTTP traffic. |
| **HTTPS / TLS** | Automated free managed certificate or custom cert. | Automated free managed certificate via Azure Container Apps ingress. | Automated Let's Encrypt via Caddy or Certbot. | Automated managed certificates provided by PaaS. |
| **Secrets Management** | Native Azure Key Vault reference integration. | Native secret store with Azure Key Vault secrets provider. | Encrypted `.env` file via `systemd` or Doppler/Vault agent. | Environment variables in PaaS dashboard or AWS Secrets Manager. |
| **Log Ingestion** | Native integration with Azure Monitor / Log Analytics. | Native Azure Log Analytics workspace integration. | Systemd journald / Docker logs forwarded via Vector or Promtail. | CloudWatch / PaaS log stream forwarding. |
| **Health Probes** | Built-in health check path configuration (`/health/live`). | Native Kubernetes-style liveness, readiness, and startup probes. | Caddy / Nginx health checking upstream or Docker healthcheck. | Platform health check endpoints. |
| **Cost Model** *(Illustrative planning estimates — not verified current provider pricing)* | B1 Basic (~$13–$20/mo) or Standard/Premium tiers. Requires current provider verification. | Consumption model (pay per vCPU-sec / GiB-sec) with free tier. Requires current provider verification. | Fixed monthly VPS cost (~$5–$25/mo depending on vendor). Requires current provider verification. | Tiered pricing (~$7–$50/mo depending on tier). Requires current provider verification. |
| **Dev Environment Parity** | High (uses standard container image matching CI). | High (uses standard container image matching CI). | High (mirrors local container runtime). | High (uses container runtime). |
| **Vendor Lock-In** | Moderate (Azure specific, but application remains standard container). | Low–Moderate (Runs standard OCI container). | Minimal (Portable to any cloud or on-premise Linux host). | Moderate (Platform-specific configurations). |
| **Suitability for this Stack** | Excellent for pairing with Azure SQL Database. | Excellent for cost-efficient bursty traffic with low baseline load. | High cost-to-performance ratio, but higher sysadmin maintenance. | Good alternative if multi-cloud is mandated by owner. |

> [!IMPORTANT]
> **Owner Decision Required:** Selection of production hosting remains **UNFINALIZED**. The local development environment strictly remains Microsoft SQL Server Express + SSMS on developer workstations at ₹0 initial cost. Cost ranges above are illustrative planning estimates only and require active provider verification prior to any commercial commitment.

---

## SECTION 4 — Production Database Strategy

### 1. Comparative Analysis of Production SQL Server Options

The production database strategy remains **UNFINALIZED — OWNER DECISION REQUIRED**. To support an objective decision without prematurely locking into any single option, the options below are evaluated across documented facts, planning assumptions, items requiring validation, and owner decision points:

| Analytical Dimension | Option A: Azure SQL Database (PaaS) | Option B: Containerized SQL Server 2022 on Linux VPS | Option C: AWS RDS for SQL Server |
| :--- | :--- | :--- | :--- |
| **Documented / Currently Verified Facts** | • pyodbc 5.3.0 + ODBC Driver 18 connection string format verified in application code.<br>• T-SQL DDL and Alembic head `4941998763bd` verified compatible with SQL Server 2022 engine.<br>• `/health/ready` probe executes `SELECT 1` ping. | • Identical container image (`mcr.microsoft.com/mssql/server:2022-latest`) currently verified in CI pipeline.<br>• 105/105 tests passing against this exact engine.<br>• Zero dialect variance from CI test baseline. | • pyodbc 5.3.0 + ODBC Driver 18 connection string format verified in application code.<br>• Standard Microsoft SQL Server T-SQL dialect supported. |
| **Planning Assumptions** | • Assumed that Azure SQL Serverless or Basic/Standard DTU tiers provide acceptable latency over TLS.<br>• Assumed that built-in automated point-in-time backups eliminate need for custom backup scripts.<br>• Assumed SLA of 99.99% for high availability. | • Assumed that Linux VPS host has sufficient IOPS and RAM (minimum 2GB for MSSQL container).<br>• Assumed that automated cron jobs with `sqlcmd` / `BACKUP DATABASE` can write to persistent volume.<br>• Assumed container restart policies guarantee process recovery. | • Assumed that AWS RDS multi-AZ provides automated failover.<br>• Assumed automated daily snapshot backups. |
| **Items Requiring Provider-Specific Validation** | • **Validation Required:** Auto-pause wakeup latency on Azure SQL Serverless (can take 30–60s on cold start, causing HTTP 503 readiness probe failure).<br>• **Validation Required:** DTU / vCore concurrent worker thread limits under peak load.<br>• **Validation Required:** Actual monthly billing against Azure calculator. | • **Validation Required:** Host OS patching procedures without database downtime.<br>• **Validation Required:** Persistent volume backup export to off-site object storage (S3/Azure Blob).<br>• **Validation Required:** Disaster recovery failover runbook and RTO measurement. | • **Validation Required:** AWS RDS Express/Web Edition licensing costs and limitations.<br>• **Validation Required:** Cross-cloud latency if application compute is hosted outside AWS. |
| **Owner Decisions Required** | • Decision to adopt Microsoft Azure ecosystem.<br>• Decision on Serverless vs. Provisioned DTU/vCore tier.<br>• Approval of recurring database service expenditure. | • Decision to accept operational sysadmin burden for database patching, backups, and OS hardening.<br>• Approval of VPS provider and backup storage destination. | • Decision to adopt AWS cloud ecosystem.<br>• Approval of AWS RDS licensing expenditure. |

> [!IMPORTANT]
> **Production Database Strategy Remains UNFINALIZED:** No database option has been designated as the final production architecture. The choice between managed PaaS (Azure SQL / AWS RDS) and self-managed container (VPS) is an explicit owner decision.

### 2. Connection Security & Authentication
- **Encryption in Transit:** In production, the connection string must mandate:
  ```
  Encrypt=yes;TrustServerCertificate=no;
  ```
  This ensures full TLS validation of the SQL Server certificate, preventing man-in-the-middle attacks.
- **Least-Privilege Database Role Separation:**
  The production database must not execute under the `sa` account. Two distinct database users are required:
  - `studio_app_user`: Member of `db_datareader` and `db_datawriter`. Permitted ONLY `SELECT`, `INSERT`, `UPDATE`, `DELETE`. Explicitly denied `ALTER`, `DROP`, `CREATE`.
  - `studio_migration_user`: Member of `db_ddladmin` and `db_owner`. Used exclusively by CI/CD migration runners during deployment; credentials never injected into runtime web workers.

### 3. Connection Pool Budgeting & Sizing
SQL Server has finite worker threads and connection memory. 
- In `app/config.py`:
  - `database_pool_size: int = 10`
  - `database_max_overflow: int = 20`
- **Multi-Worker Scaling Formula:**
  $$\text{Max DB Connections} = N_{\text{workers}} \times (\text{database\_pool\_size} + \text{database\_max\_overflow})$$
  - For a 4-worker instance: $4 \times (10 + 20) = 120\text{ potential connections}$.
  - Azure SQL Database Basic / S0 tiers cap concurrent requests (e.g., 30–60 concurrent requests).
  - **Production Recommendation:** For a low-to-moderate traffic launch, adjust pool settings to:
    `database_pool_size = 5`, `database_max_overflow = 5` per worker ($4 \times 10 = 40$ connections total).

### 4. Transient Failure Handling
SQL Server PaaS platforms experience brief transient disconnects during maintenance failovers.
- **Current Protection:** `pool_pre_ping=True` and `pool_recycle=1800` in [`app/database/connection.py:67-68`](file:///d:/Project_website/app/database/connection.py#L67-L68) detect and discard stale connections before issuing queries.
- **Production Requirement:** Add ODBC connection retry parameters to the connection string:
  ```
  ConnectRetryCount=3;ConnectRetryInterval=10;
  ```

### 5. Migration Execution Governance
- Migrations must **never** execute inside the FastAPI application startup event (`lifespan`). Running `alembic upgrade head` in multi-worker startup creates database lock contention and race conditions.
- **Production Rule:** Migration execution must occur as an isolated, pre-deployment gate in the CI/CD pipeline. The pipeline runs `alembic upgrade head` using `studio_migration_user`. If migrations fail, the deployment aborts before new application code is rolled out.

### 6. Backup, Recovery, RPO & RTO Framework
- **Backup Types:**
  - Full Backups: Weekly or Daily.
  - Differential Backups: Every 4–12 hours.
  - Transaction Log Backups: Every 5–15 minutes (enabling Point-in-Time Recovery).
- **RPO / RTO Targets:**
  > [!WARNING]
  > **PROPOSED — NOT OWNER APPROVED:** The targets below are engineering proposals only. They are **NOT** owner-approved requirements, achieved capabilities, or compliance claims:
  > - **RPO Target (PROPOSED — NOT OWNER APPROVED):** $\le 1$ hour of data loss.
  > - **RTO Target (PROPOSED — NOT OWNER APPROVED):** $\le 4$ hours to service restoration.
  > 
  > Actual RPO and RTO capabilities depend entirely on the final production database hosting model selected and funded by the owner.

---

## SECTION 5 — Secrets & Configuration Audit

### 1. Configuration vs. Secret Classification

| Setting Key | Classification | Default in Repo | Production Handling Requirement |
| :--- | :---: | :--- | :--- |
| `APP_NAME` | Configuration | `[STUDIO_NAME]` | Injected via environment variable. |
| `APP_ENV` | Configuration | `development` | Strictly set to `production`. |
| `DEBUG` | Configuration | `False` | Strictly set to `False`. |
| `BASE_URL` | Configuration | `http://localhost:8000` | Canonical production domain (`https://studio.domain.com`). |
| `SECRET_KEY` | **CRITICAL SECRET** | Insecure dev string | Cryptographically random 64-char hex string injected from Secret Vault. |
| `DATABASE_URL` | **CRITICAL SECRET** | Local SQLEXPRESS URI | Production SQL Server connection string with encrypted credentials. |
| `AI_GATEWAY_MODE` | Configuration | `mock` | Set to `live` upon commercial provider approval. |
| `AI_API_KEY` | **CRITICAL SECRET** | None (not yet added) | Injected from Secret Vault; never committed to git. |
| `AI_TIMEOUT_SECONDS`| Configuration | `10.0` | Production bounded timeout. |
| `AI_PRIMARY_MODEL` | Configuration | `studio-mock-v1` | Target commercial model identifier. |
| `LOG_FORMAT` | Configuration | `text` | Strictly set to `json` in production. |
| `SLOW_QUERY_THRESHOLD_MS` | Configuration | `500.0` | Alerting threshold. |
| `SLOW_REQUEST_THRESHOLD_MS`| Configuration | `1000.0`| Alerting threshold. |
| `SESSION_COOKIE_NAME` | Configuration | `studio_session_id` | Cookie identifier. |
| `SESSION_MAX_AGE_SECONDS` | Configuration | `2592000` (30 days) | Session TTL. |
| `SESSION_SECURE_COOKIE` | **SECURITY FLAG** | `False` | Strictly set to `True` in production. |
| `SMTP_ENABLED` | Configuration | `False` | Toggled to `True` once transactional provider is selected. |
| `SMTP_API_KEY` / `SMTP_PASSWORD` | **CRITICAL SECRET** | None | Injected from Secret Vault. |

### 2. Environment Template & `.env` Safety
- `.env` is properly listed in `.gitignore` and is not tracked in git.
- `.env.example` contains only non-sensitive dummy placeholders.
- CI pipeline in `.github/workflows/ci.yml` uses transient environment variables and does not commit secrets.

### 3. Production Secret Injection Architecture
- Secrets should never be baked into Docker images or committed to repository files.
- Recommended injection options:
  - **Option 1 (Cloud Native):** Azure Key Vault or AWS Secrets Manager referenced directly by the container service.
  - **Option 2 (Platform Environment):** Secure platform environment variables configured in hosting portal (e.g. App Service Application Settings, Container Apps Secrets).

---

## SECTION 6 — Security Production Review

An evaluation of the security controls implemented in Phase 6.1 and requirements for production readiness:

| Security Vector | Current Mitigation in Code | Residual Risk | Production Requirement | Validation Method |
| :--- | :--- | :--- | :--- | :--- |
| **HTTPS / Transport Encryption** | HSTS header injected in `app/main.py:166-167` when `app_env == "production"` or `request.url.scheme == "https"`. | Development runs plain HTTP. | Terminate TLS 1.3 at Reverse Proxy; enforce 301 redirect from HTTP to HTTPS. | SSL Labs A+ scan; curl check verifying HSTS header. |
| **Cross-Site Scripting (XSS)** | Jinja2 auto-escapes HTML variables by default. | CSP currently allows `'unsafe-inline'` for inline scripts and styles (`app/main.py:158-159`). | Refactor inline scripts/styles to external files or implement dynamic CSP nonces. | Static analysis; automated penetration test. |
| **SQL Injection (SQLi)** | SQLAlchemy 2.x Core & ORM parameterized queries across all database operations. | Raw SQL queries with string concatenation would bypass this. | Audit codebase to guarantee zero raw SQL string formatting. Current codebase uses `text("SELECT 1")` only in health probe. | Bandit AST analysis; automated SQLi test suite. |
| **Cross-Site Request Forgery (CSRF)** | Cookies configured with `samesite="lax"` (`discovery_views.py:62`). | Cross-origin top-level GETs or edge-case browser variations. | Verify `SameSite=Lax` or `Strict` on all cookies. Evaluate CSRF token for state-changing forms if cross-site embedding is allowed. | Automated CSRF regression tests. |
| **Session Cookie Hijacking** | HMAC-SHA256 signature verification; only SHA-256 hash stored in DB. | `session_secure_cookie` defaults to `False` in `app/config.py`. | Enforce `SESSION_SECURE_COOKIE=True` in production environment configuration. | Test confirming `Secure` attribute on `Set-Cookie` in HTTPS mode. |
| **Raw Token Header Leak** | `app/modules/discovery/router.py:83` sets `response.headers["X-Session-Token"] = raw_token`. | Intermediary logging proxies or browser extensions could capture raw token. | Suppress `X-Session-Token` response header in production (`app_env == "production"`). | Unit test verifying header is absent in production mode. |
| **Rate Limiting & Proxy IP Spoofing** | Sliding window rate limiter in `app/main.py:44-72`. | `_get_client_ip` trusts `X-Forwarded-For` without validating if the upstream proxy is trusted. | Configure reverse proxy (Caddy/Nginx) to strip untrusted `X-Forwarded-For` headers and set `$remote_addr`. | Spoofed header testing via curl against staging proxy. |
| **Process-Local Rate Limit Division** | In-memory `_rate_limit_store` in `app/main.py:41`. | When running $N$ worker processes, effective rate limit is multiplied by $N$. | Implement ingress rate limiting at the reverse proxy (Caddy/Nginx) or edge CDN layer. | Multi-worker concurrent flood test. |
| **Credential & PII Logging Leakage** | `SensitiveFilter` in `app/shared/logging.py` redacts bearer tokens, API keys, passwords, and email addresses. | New unformatted log messages might escape regex filters. | Strict adherence to structured logging; periodic log audit. | `test_sensitive_filter_redacts_credentials_and_pii` verified passing. |
| **AI Prompt / Response Privacy** | `scrub_pii()` runs on input problem text; zero prompt or response text is logged in telemetry. | Extremely obscure PII patterns might slip past regex scrubber. | Commercial provider enterprise contract must guarantee zero retention for model training. | Provider data protection agreement audit. |
| **Clickjacking** | `X-Frame-Options: DENY` and `frame-ancestors 'none'` in `app/main.py:152, 163`. | None identified. | Maintained in all responses. | Verified in `test_security_headers_present`. |

---

## SECTION 7 — Multi-Worker & Scaling Impact Analysis

To avoid premature distributed infrastructure (such as Redis, which remains explicitly excluded), the application's process-local components must be analyzed across three operational scales:

```
[Scale 1: Single Worker Process]
   └── In-memory rate limiting works as coded (5 req/60s).
   └── DB connection pool: 1 pool (10 conns + 20 overflow = 30 max).
   
[Scale 2: Multiple Worker Processes (Single VM / Container, e.g. 4 Uvicorn workers)]
   ├── Sessions: FULLY FUNCTIONAL (Stateless HMAC cookie + DB hash lookup).
   ├── State: FULLY FUNCTIONAL (Stateless application layer).
   ├── Telemetry / Logging: FULLY FUNCTIONAL (Atomic single-line NDJSON to shared stdout).
   ├── Database Pool: 4 pools = 4 × 30 = 120 potential connections. Sizing must be budgeted!
   └── In-Memory Rate Limiter: PARTITIONED across 4 workers.
       Effective limit per IP = 5 × 4 = 20 req/60s unless IP affinity is enforced.

[Scale 3: Multiple Container Replicas (Horizontal Scaling)]
   ├── Sessions: FULLY FUNCTIONAL across replicas sharing same SECRET_KEY & SQL Server.
   ├── Database Pool: Replicas × Workers × Pool Size must not exceed SQL Server limits.
   └── In-Memory Rate Limiter: Highly fragmented across nodes.
       MANDATORY: Rate limiting MUST be moved to Edge / Reverse Proxy tier.
```

### Technical Conclusions:
1. **Sessions are Scale-Ready:** Because session identity is cryptographically signed using HMAC-SHA256 and resolved directly against `dbo.discovery_sessions` in SQL Server, session persistence is completely stateless across processes and server instances.
2. **Rate Limiting Division:** The current in-memory rate limiter is adequate as an in-process defense-in-depth sanity check for Scale 1 and Scale 2, but **the authoritative rate limiting boundary in production must reside at the reverse proxy (Caddy/Nginx) or Edge CDN**. This satisfies the constraint of excluding Redis while preventing abuse.
3. **Database Pool Budgeting:** To prevent exhausting SQL Server connections when running multiple workers, `database_pool_size` should be set to `5` and `database_max_overflow` to `5` in production.

---

## SECTION 8 — AI Production Readiness & Decision Matrix

### 1. Current AI Gateway Posture
- **Protocol Abstraction:** `app/ai_gateway/interface.py` defines `IAIProvider` and `IAIServiceGateway`.
- **Active Adapter:** Currently operates via `MockAIProvider` with heuristic fallback catalogs (`fallback_catalog.py`).
- **Safety Controls:** Problem text is passed through `scrub_pii()` before provider dispatch.
- **Resilience:** Async execution bounded by `ai_timeout_seconds` (10.0s). Catches `asyncio.TimeoutError`, `ValidationError`, and generic `Exception`, seamlessly falling back to deterministic business heuristics.
- **Zero-Leakage Telemetry:** Emits `ai_completion` and `ai_fallback` events recording latency, model name, and source, with zero prompt or response text exposed to logs.

### 2. Commercial Provider Selection Decision Matrix

No commercial provider has been finalized. The table below presents an objective evaluation framework for owner selection:

| Evaluation Criteria | Azure OpenAI Service | OpenAI Direct API | Anthropic Claude API | AWS Bedrock | Google Cloud Vertex AI |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Enterprise Data Privacy** | Strict zero-retention; data does not train base models. Covered by Microsoft Enterprise BAA. | Zero-data-retention available for API customers; enterprise BAA available. | Zero-retention for API; enterprise terms available. | Strict enterprise zero-retention; AWS compliance envelope. | Enterprise compliance; models do not train on customer data. |
| **Data Residency** | Region-specific deployment (e.g. Central India, East US, West Europe). | Global endpoints; limited EU data residency options. | Primary US endpoints. | Region-specific deployments (including India/Mumbai). | Region-specific deployments (including India/Mumbai). |
| **Structured Output Support** | Native JSON Schema / Structured Outputs (`response_format: json_schema`). | Native JSON Schema / Structured Outputs. | Native Tool Use / Structured JSON outputs. | Native JSON schema support depending on chosen model. | Structured JSON schema enforcement. |
| **Latency & SLA** | High availability with Azure enterprise SLA and provisioned throughput options. | Standard commercial API SLA; occasional peak-hour queuing. | Strong performance; enterprise SLAs available. | AWS-backed enterprise availability. | Google Cloud enterprise SLA. |
| **Cost Model** | Pay-per-token or Provisioned Throughput Units (PTU). Pricing requires current verification. | Pay-per-token with tier-based prepayment or monthly invoicing. Pricing requires current verification. | Pay-per-token with tier-based billing. Pricing requires current verification. | Pay-per-token via consolidated AWS monthly bill. Pricing requires current verification. | Pay-per-token via consolidated GCP monthly bill. Pricing requires current verification. |
| **SDK & Ecosystem** | `openai` Python SDK (Azure configuration) or REST API. | `openai` official Python SDK or REST API. | `anthropic` official Python SDK or REST API. | `boto3` SDK or AWS REST API. | `google-cloud-aiplatform` SDK. |
| **Architectural Fit** | Synergistic if hosting on Azure App Service / Azure SQL. | Provider-neutral; works across any host. | Provider-neutral; works across any host. | Synergistic if hosting on AWS infrastructure. | Synergistic if hosting on GCP infrastructure. |

### 3. Prerequisites for Commercial AI Activation
Before activating any commercial provider in a future phase:
1. Owner selection of preferred provider and geographic region.
2. Creation of production API credentials and spend quota caps (e.g., hard cap of $50/month).
3. Implementation of provider adapter conforming to `IAIProvider` in `app/ai_gateway/`.
4. Integration of exponential backoff retry for transient 429/503 HTTP responses.

---

## SECTION 9 — Email & Contact Production Readiness

### 1. Audit of Current Contact Workflow
- **Route:** `POST /contact` in [`app/routers/web.py:240-307`](file:///d:/Project_website/app/routers/web.py#L240-L307).
- **Validation:** Enforces non-empty name, valid email format regex, and non-empty message.
- **Logging & Telemetry:** Logs sanitized message length (corporate email is redacted). Emits `contact_submitted` telemetry event.

> [!CAUTION]
> **Production Launch Requirement / Future Implementation Item:**
> The current `/contact` workflow validates and emits telemetry but does **NOT** currently provide durable inquiry persistence in Microsoft SQL Server. In contrast to Discovery Stage 5 (`/discovery/unlock`), which writes a `Lead` record to `dbo.leads` and consent to `dbo.lead_consents`, the contact form relies purely on in-memory request processing. Because `SMTP_ENABLED=False`, inquiries submitted via `/contact` may currently be unrecorded if email dispatch is disabled or fails.
> 
> This is strictly documented as a **Production launch requirement / future implementation item**. Zero migrations or database schema modifications are authorized or executed in this planning phase.

### 2. Required Future Remediations (Pre-Launch Scope)
1. **Contact Inquiry Persistence (Future Phase):** A production migration in a future phase must establish either:
   - Reuse of `dbo.leads` with a new `lead_source = 'contact_form'` attribute, or
   - A dedicated `dbo.contact_inquiries` table capturing `full_name`, `corporate_email`, `company_name`, `project_scope`, and `message` with timestamp and IP hash.
2. **Transactional Email Dispatcher (Future Phase):** Implement a transactional email service behind an interface (`IEmailDispatcher`), decoupled from the web request loop via background execution.
3. **Anti-Spam Controls:** In addition to the existing IP rate limiter (5 req/60s), add a hidden honeypot form field to deflect automated bots without adding third-party tracking scripts.

### 3. Transactional Email Provider Comparison

| Provider | Delivery Model | Pricing Tier *(Illustrative planning estimates — not verified current provider pricing)* | Python SDK / API | Data Privacy / Tracking |
| :--- | :--- | :--- | :--- | :--- |
| **Resend** | HTTPS REST API | Free tier (~3,000 emails/mo, 100/day); ~$20/mo for 50k. Requires current verification. | Lightweight REST API or `resend` SDK. | Modern, developer-centric, minimal tracking. |
| **Postmark** | HTTPS REST API / SMTP | Free trial (100 emails); ~$15/mo for 10k emails. Requires current verification. | REST API with high deliverability reputation. | Strict transactional focus; high privacy standard. |
| **SendGrid** | HTTPS REST API / SMTP | Free tier (100 emails/day); ~$19.95/mo for 50k. Requires current verification. | Widely supported Python SDK. | Standard enterprise; heavier marketing tooling. |
| **Amazon SES** | HTTPS / SMTP | ~$0.10 per 1,000 emails. Requires current verification. | Native `boto3`. | Lowest cost; requires domain verification sandbox exit. |
| **Azure Communication Services** | HTTPS REST API | ~$0.00025 per email (~$0.25 per 1,000). Requires current verification. | Azure Python SDK. | Consolidated billing if hosting on Azure. |

---

## SECTION 10 — Observability & Alerting Framework

Building on the Phase 6.2.3 NDJSON observability foundation, the production observability strategy operates with zero third-party tracking scripts and zero database write contention:

### 1. Production Log & Telemetry Pipeline
```
[Application stdout (Single-line NDJSON)]
                   │
                   ▼
[Container Runtime Log Collector (e.g., Docker / Container Apps / Vector)]
                   │
                   ├──> Central Log Store (Azure Log Analytics / CloudWatch Logs)
                   │         │
                   │         ▼
                   │    [Scheduled KQL / CloudWatch Metric Queries]
                   │         │
                   │         ▼ (Threshold Exceeded)
                   │    [Alert Rule Notification]
                   │         │
                   │         ▼
                   └────> [Operational Notification Destination (Email / Slack Webhook)]
```

### 2. Operational Signals & Proposed Alert Thresholds

> [!IMPORTANT]
> **Owner Approval Required:** The alert conditions and thresholds below are engineering proposals designed for high-signal, low-noise operations. Final alert thresholds and destination inboxes require owner approval.

| Signal Name | Source Metric / Log Event | Proposed Severity | Proposed Alert Trigger Condition | Operational Action |
| :--- | :--- | :---: | :--- | :--- |
| **Database Outage** | `GET /health/ready` returns HTTP 503 | **SEV-1** | 2 consecutive probe failures (30s window). | Page on-call architect; verify SQL Server status and network connectivity. |
| **Elevated HTTP 5xx Rate** | HTTP response status codes $\ge 500$ | **SEV-2** | $> 5\%$ of total requests failing over a 5-minute rolling window. | Inspect application exception logs; verify downstream service health. |
| **High Query Latency** | `event == "slow_sql_query"` ($>500\text{ms}$) | **SEV-3** | $> 10$ slow query events in a 10-minute window. | Investigate SQL Server CPU/memory and query execution plans. |
| **AI Provider Outage / Fallback Spike** | `event == "ai_fallback"` | **SEV-3** | Fallback rate $> 20\%$ over a 15-minute window. | Verify commercial AI provider API status and credit balance. |
| **Abuse / Rate Limit Flooding** | `event == "rate_limit_exceeded"` | **SEV-4** | $> 50$ rate limit violations from multiple IPs in 5 minutes. | Investigate potential scraping or automated spam campaign at reverse proxy. |
| **Slow HTTP Requests** | `event == "slow_http_request"` ($>1000\text{ms}$)| **SEV-4** | $> 5\%$ of requests exceeding 1.0s over 15 minutes. | Profile application endpoints; evaluate worker thread contention. |

---

## SECTION 11 — Backup, Disaster Recovery & Incident Response Framework

### 1. Database Backup & Restore Plan
- **Backup Strategy for SQL Server:**
  - Automated full backup executed daily during low-traffic hours (e.g. 02:00 UTC).
  - Automated transaction log backups every 15 minutes (if running full recovery model).
  - Off-site immutable storage: Backups stored in geo-redundant object storage with encryption at rest (AES-256).
- **Restore Testing Drills:**
  - Automated restore verification drill executed monthly into a transient scratch database to empirically prove backup integrity and measure actual restoration duration.

### 2. Disaster Recovery Scenarios & Playbooks

| Disaster Scenario | Failure Mode | Recovery Procedure |
| :--- | :--- | :--- |
| **Primary Host Failure** | Compute VM or container cluster crashes. | Orchestrator auto-spawns replacement container instance; DNS/Ingress shifts traffic to healthy replica. |
| **Database Corruption / Data Loss** | Table corruption, accidental truncation, or bad migration. | Execute Point-in-Time Recovery (PITR) to timestamp immediately preceding corruption. Point application to restored database. |
| **Cryptographic Secret Leak** | `SECRET_KEY` or database credentials exposed. | 1. Immediately rotate secret in Secret Vault.<br>2. Deploy container with updated secret.<br>3. Invalidate active discovery sessions (users restart session). |
| **DNS / CDN Outage** | External DNS provider failure. | Shift nameservers to secondary DNS provider with pre-staged zone records. |

### 3. Database Migration Rollback Limitations
- **Alembic Downgrade Risk:** While `migrations/versions/4941998763bd_initial_mvp_foundation.py` contains a valid `downgrade()` function (`DROP TABLE` for all 10 tables), executing `alembic downgrade -1` in production is **DESTRUCTIVE** and causes permanent data loss.
- **Production Governance Rule:** In production, forward-only migrations must be preferred. If an erroneous migration is deployed, a compensating forward migration (`alembic revision`) must be written and applied rather than rolling back destructive DDL.

### 4. Incident Severity Levels
- **SEV-1 (Critical):** Complete site outage or database down; public traffic cannot access website or discovery engine. Immediate response.
- **SEV-2 (Major):** Discovery engine or lead capture failing, but static marketing pages remain accessible. Response within 1 hour.
- **SEV-3 (Moderate):** Commercial AI provider failing (operating on fallback heuristics) or intermittent slow queries. Response within 4 hours.
- **SEV-4 (Minor):** Cosmetic UI issue, minor telemetry anomaly, or isolated non-impacting error. Addressed during business hours.

---

## SECTION 12 — CI/CD Production Promotion Pipeline

### 1. Production Promotion Lifecycle Flow

```
[ Developer Commit / PR ]
           │
           ▼
[ GitHub Actions CI Pipeline ]
   ├── Step 1: Lint & Code Quality (Ruff)
   ├── Step 2: Security Static Analysis (Bandit)
   ├── Step 3: Dependency Vulnerability Audit (pip-audit)
   ├── Step 4: Spin up SQL Server 2022 Linux Container
   ├── Step 5: Execute Alembic Migrations against Real MSSQL
   ├── Step 6: Execute Full Test Suite (105 tests)
   └── Step 7: Build & Scan Production OCI Container Image
           │
           ▼ (Triggered only on push to `main`)
[ Staging Deployment Gate (Automated) ]
   ├── Deploy image to Staging Environment
   ├── Run DB migrations against Staging SQL Server
   └── Execute Automated Smoke Tests & /health/ready probe
           │
           ▼
[ Production Deployment Gate (MANUAL OWNER APPROVAL) ]
   ├── Owner signs off in GitHub Environment Protection Rule
   ├── Pre-deployment DB migration execution
   ├── Blue/Green or Rolling Deployment to Production Compute
   ├── Post-deployment Health Check validation (/health/ready)
   └── AUTOMATIC ROLLBACK if health probe fails within 60 seconds
```

### 2. CI/CD Governance & Separation of Environments
- **Environment Protection Rules:** Production deployments must require explicit manual approval from the repository owner.
- **Secret Separation:** GitHub Actions secrets must be partitioned by environment (`development`, `staging`, `production`). Production credentials must never be accessible to pull request CI runs.

---

## SECTION 13 — Zero-Downtime & Migration Safety

### 1. Application Layer Zero-Downtime Readiness
- **Stateless Architecture:** The FastAPI modular monolith maintains no process-local user state. Requests can be dynamically routed to old or new containers during a rolling deployment without dropping sessions.
- **Graceful Connection Draining:** On receiving `SIGTERM`, the application stops accepting new requests, completes in-flight requests within a 30-second grace period, and calls `dispose_engine()` to cleanly close database connections.

### 2. Database Schema Migration Safety (Expand/Contract Pattern)
To ensure rolling deployments never break in-flight requests running against older application code, database migrations must adhere strictly to the **Expand/Contract Pattern**:

```
[ Phase 1: Expand (Pre-Deployment) ]
  - Add new nullable columns, new tables, or columns with safe defaults.
  - DO NOT rename or drop existing columns.
  - Apply migration to production SQL Server.

[ Phase 2: Deploy Application ]
  - Roll out new application version.
  - New version begins writing to both old and new schema, or new schema only.
  - Old version continues functioning without error.

[ Phase 3: Contract (Post-Deployment / Future Release) ]
  - After all older container instances are decommissioned and verified stable,
    run a follow-up migration to remove deprecated columns or tables.
```

---

## SECTION 14 — Performance & Capacity Validation Plan

### 1. Empirical Performance Targets (Proposed)
All performance metrics must be validated empirically; no speculative performance claims are made:

| Metric | Target (p50) | Target (p95) | Target (p99) | Validation Method |
| :--- | :---: | :---: | :---: | :--- |
| **Static / Marketing Pages** | $< 30\text{ ms}$ | $< 100\text{ ms}$ | $< 250\text{ ms}$ | Non-destructive load test against staging (`/`, `/services`, `/about`). |
| **Discovery Session Resumption** | $< 50\text{ ms}$ | $< 150\text{ ms}$ | $< 350\text{ ms}$ | Authenticated GET `/discovery` with active cookie. |
| **Stage 1 Problem Submission** | $< 80\text{ ms}$ | $< 250\text{ ms}$ | $< 500\text{ ms}$ | POST `/discovery/problem` with PII scrubbing and DB write. |
| **SQL Server Query Execution** | $< 5\text{ ms}$ | $< 25\text{ ms}$ | $< 100\text{ ms}$ | Monitored via SQLAlchemy Core cursor hooks (`slow_query_threshold_ms = 500`). |
| **AI Gateway Generation (Live)** | $< 1500\text{ ms}$ | $< 3500\text{ ms}$ | $< 8000\text{ ms}$ | Upstream provider round-trip with 10.0s hard timeout cutoff. |

### 2. Capacity & Resource Sizing Formula
- **Worker Memory Footprint:** Each Uvicorn worker process requires approximately 80–120 MB RAM under load. A 2-worker container requires $\sim 512\text{ MB}$ to $1\text{ GB}$ RAM.
- **Database Connection Capacity:** 
  $$\text{Total Connections} = \text{Instances} \times \text{Workers per Instance} \times (\text{pool\_size} + \text{max\_overflow})$$
  With 1 instance, 2 workers, `pool_size=5`, `max_overflow=5`, total peak database connections is $2 \times 10 = 20$, well within entry-level SQL Server limits.

---

## SECTION 15 — Production Environment Matrix

| Parameter / Layer | Development (Current) | Testing / CI (Current) | Staging (Proposed) | Production (Proposed) |
| :--- | :--- | :--- | :--- | :--- |
| **Operating System** | Windows 11 (Developer Local) | Ubuntu Latest (GitHub Actions) | Linux (Ubuntu / Alpine Container) | Linux (Ubuntu / Alpine Container) |
| **Python Version** | Python 3.13.7 virtualenv | Python 3.13 (`actions/setup-python`) | Python 3.13 Container | Python 3.13 Container |
| **Database Instance** | Microsoft SQL Server 2022 Express (`.\SQLEXPRESS`) | SQL Server 2022 Linux Container (`127.0.0.1:1433`) | Isolated Staging SQL Server (Azure SQL / Container) | Production SQL Server (Azure SQL / Dedicated VPS) |
| **Database Encryption** | `TrustServerCertificate=yes` | `TrustServerCertificate=yes` | `Encrypt=yes;TrustServerCert=no` | `Encrypt=yes;TrustServerCert=no` |
| **Secrets Storage** | Local `.env` file | GitHub Actions Secrets | Cloud Secret Vault / App Config | Cloud Secret Vault / App Config |
| **`APP_ENV` Value** | `development` | `testing` | `staging` | `production` |
| **`DEBUG` Flag** | `True` | `False` | `False` | `False` |
| **`SESSION_SECURE_COOKIE`** | `False` | `False` | `True` | `True` |
| **AI Gateway Mode** | `mock` (`MockAIProvider`) | `mock` (`MockAIProvider`) | `live` or `mock` (Staging key) | `live` (Commercial Provider) |
| **AI Spend Quota** | None ($0) | None ($0) | Bounded test quota ($10/mo) | Bounded production quota (e.g. $50/mo) |
| **Email Dispatcher** | `SMTP_ENABLED=False` | `SMTP_ENABLED=False` | Sandbox Email / Log Egress | Transactional Email API |
| **Log Format** | `text` (Console) | `text` (Pytest capture) | `json` (NDJSON to stdout) | `json` (NDJSON to stdout) |
| **Deployment Method** | Local execution | Automated GitHub Actions CI | CD Pipeline to Staging Host | CD Pipeline with Owner Approval |
| **Access Control** | Developer local machine | GitHub Repository Committer | Private IP / Staging Auth Gate | Public Internet via Edge / CDN |

---

## SECTION 16 — Cost Model Framework

> [!CAUTION]
> **CRITICAL PRICING NOTICE:**
> All production cost figures listed below are **illustrative planning estimates — not verified current provider pricing**.
> They do not represent guaranteed, fixed, current, or committed costs. No current pricing evidence is asserted in this report. Prior to implementation or budget commitment, exact current provider pricing must be independently verified against active cloud provider rate cards (Azure, AWS, Hetzner, OpenAI, Resend, etc.).

| Cost Domain | Development (Current) | CI / Testing (Current) | Production Tier 1: Lean *(Illustrative Planning Estimate — Not Verified Current Pricing)* | Production Tier 2: Managed PaaS *(Illustrative Planning Estimate — Not Verified Current Pricing)* |
| :--- | :---: | :---: | :--- | :--- |
| **Application Compute** | ₹0 (Local PC) | $0 (GitHub Free Minutes) | ~$5 – $12 / mo (Hetzner / DO VPS, 2 vCPU, 4GB) — *Unverified estimate* | ~$15 – $35 / mo (Azure App Service B1 / Container Apps) — *Unverified estimate* |
| **SQL Server Database** | ₹0 (MSSQL Express) | $0 (Free CI Container) | $0 (Container on VPS) or ~$5–$15/mo (Azure SQL Serverless) — *Unverified estimate* | ~$15 – $40 / mo (Azure SQL Database Basic/Standard) — *Unverified estimate* |
| **Domain & DNS** | ₹0 | $0 | ~$10 – $15 / year (~$1/mo) — *Unverified estimate* | ~$10 – $15 / year (~$1/mo) — *Unverified estimate* |
| **TLS / SSL Certificates** | ₹0 | $0 | $0 (Let's Encrypt / Certbot / Cloudflare) | $0 (Azure Managed Cert / Cloudflare) |
| **Commercial AI Token Usage**| ₹0 (Mock Provider) | $0 (Mock Provider) | Variable: ~$10 – $30 / mo (Token volume dependent) — *Unverified estimate* | Variable: ~$10 – $30 / mo (Token volume dependent) — *Unverified estimate* |
| **Transactional Email** | ₹0 (Disabled) | $0 (Disabled) | $0 (Resend / SendGrid Free Tier up to limits) | ~$10 – $20 / mo (Postmark / Resend paid tier) — *Unverified estimate* |
| **Log Storage & Monitoring** | ₹0 (Local stdout) | $0 (CI log tail) | $0 – $5 / mo (Local logs / Free CloudWatch/Azure tier) — *Unverified estimate* | ~$5 – $15 / mo (Azure Log Analytics / Datadog basic) — *Unverified estimate* |
| **Total Estimated Monthly** | **₹0** | **$0** | **~$20 – $50 / month**<br>*(Illustrative planning estimate — not verified current provider pricing)* | **~$50 – $120 / month**<br>*(Illustrative planning estimate — not verified current provider pricing)* |

---

## SECTION 17 — Production Readiness Checklist

| Area | Current Repository State | Required Production Action | Owner Decision Required? | Proposed Validation Method | Target Future Phase |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Production Dockerfile** | MISSING | Create multi-stage production Dockerfile (Python 3.13 slim, msodbcsql18, non-root user). | No (Technical spec) | Container build & smoke test in CI. | Phase 6.2.5 |
| **Minimal Runtime Dependencies** | PARTIALLY READY (flat `requirements.txt`) | Split into `requirements/base.txt` and `requirements/dev.txt`. | No (Technical spec) | Clean install and test in CI. | Phase 6.2.5 |
| **Hosting Platform Selection** | UNFINALIZED | Select production compute provider (Azure vs. Linux VPS vs. other). | **YES** | Owner approval of hosting platform. | Phase 6.2.5 |
| **SQL Server Production Host** | UNFINALIZED | Select and provision production SQL Server model (PaaS vs Container VPS). | **YES** | Live pyodbc connectivity check. | Phase 6.2.5 |
| **Production Secrets Injection** | PARTIALLY READY (`SecretStr` active) | Configure Secret Store / Vault and inject production `SECRET_KEY` & DB URL. | **YES** | Staging environment startup test. | Phase 6.2.6 |
| **Trusted Proxy Configuration** | PARTIALLY READY | Configure trusted proxy IP handling in FastAPI to safely parse `X-Forwarded-For`. | No (Technical spec) | Spoofed header testing via curl. | Phase 6.2.6 |
| **Cookie HTTPS Enforcement** | PARTIALLY READY (`session_secure_cookie=False`) | Enforce `SESSION_SECURE_COOKIE=True` in staging and production settings. | No (Technical spec) | Inspect Set-Cookie header in staging. | Phase 6.2.6 |
| **Contact Form DB Persistence** | PARTIALLY READY (no DB write) | **Production launch requirement / future implementation item:** Add inquiry persistence to `dbo.leads` or `dbo.contact_inquiries`. | No (Technical requirement) | Automated database integration test. | Phase 6.2.6 |
| **Static Asset Caching** | PARTIALLY READY (no cache headers) | Configure reverse proxy or middleware for 1-year immutable static caching. | No (Technical spec) | Verify `Cache-Control` header on `/static/*`. | Phase 6.2.6 |
| **Commercial AI Provider** | PARTIALLY READY (`MockAIProvider` active) | Select provider, implement `IAIProvider` adapter, configure spend quota. | **YES** | Staging AI generation test. | Phase 6.2.7 |
| **Transactional Email Provider** | PARTIALLY READY (`SMTP_ENABLED=False`) | Select email vendor, implement dispatcher, configure sender domain DNS (SPF/DKIM).| **YES** | Live test email dispatch verification. | Phase 6.2.7 |
| **Backup & Restore Drills** | MISSING | Establish automated SQL Server backup schedule and execute verified restore drill. | **YES** (RPO/RTO: PROPOSED — NOT OWNER APPROVED) | Successful restore to scratch DB. | Phase 6.2.8 |
| **Operational Alert Routing** | PARTIALLY READY (NDJSON emitted) | Wire container logs to log forwarder and configure alert destinations. | **YES** (Thresholds) | Trigger artificial 500 error; verify alert. | Phase 6.2.8 |
| **Performance Load Benchmarking**| MISSING | Run empirical load test against staging to validate p95 latency targets. | No (Technical spec) | Automated locust/k6 test run. | Phase 6.2.8 |

---

## SECTION 18 — Future Phase Breakdown

To maintain strict governance and prevent unreviewed changes, work following this planning report is partitioned into focused, dependency-aware phases:

```
[Phase 6.2.4: Production Readiness Planning] <── (CURRENT PHASE - PLANNING ONLY)
       │
       ▼ (Awaiting Owner Review & Authorization)
[Phase 6.2.5: Deployment Foundation & Containerization]
  - Multi-stage minimal production Dockerfile (Python 3.13 + ODBC Driver 18).
  - Dependency segregation (base.txt vs dev.txt).
  - Reverse proxy configuration specification (Caddy / Nginx).
  - Process supervisor configuration (Uvicorn / Gunicorn).
       │
       ▼ (Owner Gate)
[Phase 6.2.6: Production Security Hardening & Staging Provisioning]
  - Contact form database persistence migration (Production launch requirement).
  - Trusted proxy IP middleware configuration.
  - Suppression of X-Session-Token header in production mode.
  - Staging environment infrastructure provisioning (per owner hosting decision).
       │
       ▼ (Owner Gate)
[Phase 6.2.7: External Integrations (Commercial AI & Transactional Email)]
  - Implement commercial AI provider adapter behind `IAIProvider`.
  - Configure AI usage budget caps and exponential retry backoff.
  - Implement transactional email dispatcher behind `IEmailDispatcher`.
       │
       ▼ (Owner Gate)
[Phase 6.2.8: Production Launch Readiness & Operational Drills]
  - End-to-end staging smoke and non-destructive load benchmarking.
  - Backup and restore disaster recovery drill.
  - Production environment rollout, DNS cutover, and post-launch verification.
```

---

## SECTION 19 — Owner Decisions Required

The following decisions require owner review and explicit direction:

1. **Production Hosting Platform:** Select between **Azure App Service**, **Azure Container Apps**, or **Dedicated Linux VPS** (Section 3).
2. **Production SQL Server Strategy:** Select between **Azure SQL Database (PaaS)** or **Containerized SQL Server on Linux VPS** (Section 4). Strategy remains UNFINALIZED.
3. **Commercial AI Provider & Model:** Select primary commercial LLM partner (**Azure OpenAI**, **OpenAI Direct**, **Anthropic**, **AWS Bedrock**, or **Google Vertex AI**) and approve monthly spend ceiling (Section 8).
4. **Transactional Email Provider:** Select provider (**Resend**, **Postmark**, **SendGrid**, **AWS SES**, or **Azure Communication Services**) for customer inquiries and architect alerts (Section 9).
5. **RPO & RTO Targets:** Formally review and decide on business Recovery Point Objective (RPO $\le 1$ hour: **PROPOSED — NOT OWNER APPROVED**) and Recovery Time Objective (RTO $\le 4$ hours: **PROPOSED — NOT OWNER APPROVED**) (Section 4 & 11).
6. **Alert Notification Destination:** Designate the operational email address or webhook endpoint for SEV-1 and SEV-2 system alerts (Section 10).
7. **Production Domain Name:** Confirm canonical production apex domain and DNS management provider (Section 2 & 15).
8. **Monthly Infrastructure Budget Ceiling:** Confirm target monthly operational budget envelope (Illustrative planning estimates e.g. ~$20 – $50/mo or ~$50 – $120/mo; requires current provider pricing verification prior to commitment) (Section 16).

---

## SECTION 20 — Risks, Blockers & Open Questions

### 1. Blockers (Must be resolved before production deployment can occur)
- **BLK-01: Hosting Provider Unselected:** No production host is provisioned or selected.
- **BLK-02: Production SQL Server Unprovisioned:** No production SQL Server instance exists to accept migrations. Strategy remains UNFINALIZED.
- **BLK-03: Commercial AI Provider Unselected:** System operates on `MockAIProvider`; live AI intake requires commercial API keys and approved billing.
- **BLK-04: Contact Form Durable Persistence (Production Launch Requirement / Future Implementation Item):** The current `/contact` workflow validates input and emits telemetry, but does not provide durable inquiry persistence in SQL Server. Inquiries may be unrecorded while `SMTP_ENABLED=False`. Must be implemented in a future phase prior to launch.

### 2. Risks (Technical and operational risks requiring active mitigation)
- **RSK-01: Process-Local Rate Limiting Division:** In-memory rate limiting divides across workers unless enforced at reverse proxy tier.
- **RSK-02: Database Connection Pool Exhaustion:** Excessive worker counts on low-tier SQL Server plans could exhaust database worker threads.
- **RSK-03: AI Provider Latency / Rate Limits:** Upstream LLM latency spikes could degrade user experience if fallback heuristics are not seamlessly triggered.
- **RSK-04: Untrusted `X-Forwarded-For` Spoofing:** Direct exposure of FastAPI without a trusted reverse proxy allows client IP spoofing.

### 3. Open Questions
- **OPN-01:** Does the owner prefer an integrated single-vendor ecosystem (e.g. all Azure: App Service + Azure SQL + Azure OpenAI) or a cost-optimized multi-vendor setup (e.g. Hetzner VPS + OpenAI Direct + Resend)?
- **OPN-02:** What is the legal corporate entity name and registration details to finalize in `/privacy` and `/terms` prior to public launch?

### 4. Non-Blocking Follow-Ups
- **FOL-01:** Implement cache-busting asset query parameters or asset fingerprinting for `/static/css/main.css`.
- **FOL-02:** Tighten Content Security Policy (CSP) by refactoring minor inline scripts in templates to use nonces.

---

## Final Governance Status

**PHASE 6.2.4 PLANNING CORRECTED — AWAITING OWNER APPROVAL**

*Strict Implementation Boundary Maintained: Zero application code modified, zero migrations created, zero dependencies installed, zero cloud infrastructure deployed.*
