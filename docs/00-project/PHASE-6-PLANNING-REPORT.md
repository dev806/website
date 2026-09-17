# PHASE 6 — RIGOR, SECURITY & RELIABILITY
## PLANNING & GOVERNANCE AUDIT REPORT (RECONCILED & CORRECTED)

**Document ID:** `DOC-PLAN-6.0-001`  
**Phase:** Phase 6 (Planning & Governance Audit Stage — Reconciliation Pass)  
**Status:** COMPLETE — RECONCILED & CORRECTED — AWAITING OWNER APPROVAL  
**Governance Horizon:** Rigor, Security, Reliability, DevOps & Telemetry  

---

## EXECUTIVE SUMMARY

Following owner review, this **Phase 6 Planning Correction & Governance Reconciliation Pass** audits and aligns the Phase 6 implementation plan with the **ACTUAL current codebase, active endpoints, empirical test metrics, and authoritative project decisions**.

Phase 6 elevates the application from a **"working MVP"** to a **"secure, testable, observable, and deployment-ready system"** without over-engineering, without adding Redis or complex SaaS platforms, and without breaking completed Phase 5 deliverables.

---

## PHASE 6 PLANNING CORRECTIONS & GOVERNANCE RECONCILIATION

---

### 1. CORRECTED DISCOVERY & PUBLIC ENDPOINT INVENTORY

Replacing legacy generic references (such as `/discovery/submit`) with the **exact active router endpoint inventory** from `app/routers/discovery_views.py` and `app/routers/web.py`:

| Endpoint Path | Method | Access Level | State Mutating | Rate Limit Req. | CSRF Req. | Abuse Risk | Idempotency | Validation Requirement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET /discovery` | GET | Public | No | Low (30/min) | No | Low | Idempotent | Validates session cookie or creates new |
| `POST /discovery/start` | POST | Public | Yes | Low (10/min) | Yes | Low | Idempotent | Resets session state to `START` |
| `POST /discovery/problem` | POST | Public | Yes | **High (5/min)** | Yes | **High** (Token drain)| 20–2000 chars + PII Scrub |
| `POST /discovery/answers` | POST | Session | Yes | Medium (15/min)| Yes | Medium | Non-idempotent | Validates radio selections |
| `GET /discovery/stage/opportunity-map` | GET | Session | No | Low (30/min) | No | Low | Idempotent | Requires FSM `MAP_SYNTHESIZED` |
| `GET /discovery/stage/{stage_name}` | GET | Session | No | Low (30/min) | No | Low | Idempotent | Validates stage permissions |
| `POST /discovery/unlock` | POST | Session | Yes | **High (5/min)** | Yes | **High** (Lead capture)| Name, Email regex, Consent=True |
| `POST /discovery/review` | POST | Session (Unlocked)| Yes | **High (5/min)** | Yes | Medium | Non-idempotent | Requires `is_unlocked=true` |
| `POST /discovery/backtrack` | POST | Session | Yes | Medium (15/min)| Yes | Low | Idempotent | Validates target stage |
| `POST /contact` | POST | Public | Yes | **High (5/min)** | Yes | **High** (Form spam) | Non-idempotent | Name, Email regex, Msg + PII Scrub |

*Plus 16 public GET HTML/Asset endpoints (`/`, `/services`, `/services/{slug}`, `/solutions`, `/how-we-work`, `/about`, `/contact`, `/privacy`, `/terms`, `/security`, `/robots.txt`, `/sitemap.xml`).*

---

### 2. RATE LIMITING DECISION ANALYSIS (ZERO REDIS)

Comparing rate-limiting options without adding Redis infrastructure:

- **Approach A (Recommended for MVP)**: **Native FastAPI In-Memory Sliding Window Middleware**.
  - *Mechanism*: In-memory sliding window counter dictionary (`defaultdict(list)`) keyed by client IP and route path.
  - *Pros*: Zero external dependencies, **₹0 cost**, sub-millisecond execution, simple Pytest testability.
  - *Limitation*: Memory counter resets on process restart and is bounded to single-worker processes.
- **Approach B**: **Reverse-Proxy / Edge Rate Limiting** (Cloudflare / Azure Front Door / IIS / Nginx).
  - *Mechanism*: Offloads rate limiting to edge network prior to application entry.
  - *Recommendation*: Use Approach A for local development and single-instance environments; offload to Approach B for multi-worker production deployments without adding Redis.

---

### 3. SECURITY HEADER STRATEGY (COMPATIBLE WITH HTMX & ALPINE.JS)

Security headers are designed to protect the site without breaking Jinja2, HTMX swaps, Alpine.js reactivity, or inline SVGs:

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; form-action 'self';
```

*Note: `'unsafe-inline'` is required for Alpine.js dynamic event evaluation (`@click`, `@keydown.escape`) and HTMX inline event handling.*

---

### 4. SQL SERVER CI STRATEGY

To maintain **100% database dialect fidelity (`BD-001`)**, the CI pipeline does **NOT** replace Microsoft SQL Server with SQLite or PostgreSQL.

The GitHub Actions workflow (`.github/workflows/ci.yml`) utilizes an official Microsoft SQL Server 2022 Linux container service container:

```yaml
# Conceptual GitHub Actions Workflow
name: CI Pipeline
on: [push, pull_request]
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
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - run: pip install -r requirements.txt
      - run: bandit -r app/
      - run: alembic upgrade head
      - run: pytest tests/ -v && pytest spikes/test_sprint0_suite.py -v
```

- **Cost**: **$0** (Runs on GitHub Actions free runner minutes).
- **Fidelity**: 100% dialect fidelity against real SQL Server T-SQL engine.

---

### 5. PROVIDER-NEUTRAL PRODUCTION DEPLOYMENT MATRIX

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

### 6. DOCUMENTATION DRIFT MATRIX

Reconciling historical documentation drafts against active implementation:

| Historical Document Concept | Legacy Document Location | Current Codebase Implementation | Governance Classification | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Next.js / React** | `DOC-WEB-001` (legacy draft) | Python 3.13 + FastAPI + Jinja2 + HTMX + Alpine.js | **STALE — REQUIRES UPDATE** | Update doc to reflect approved Python-first stack (`BD-015`) |
| **PostgreSQL / Prisma** | `DOC-DB-001` (legacy draft) | Microsoft SQL Server + SQLAlchemy 2.x + Alembic | **STALE — REQUIRES UPDATE** | Reconcile to SQL Server (`BD-001`) |
| **Vercel / Supabase** | `DOC-DEV-001` (legacy draft) | Local SQL Server + Uvicorn (Prod TBD) | **STALE — REQUIRES UPDATE** | Reconcile to provider-neutral deployment matrix |
| **Redis / Celery** | `DOC-ARCH-016` | Threadpool Async + Synchronous SQL Server | **STALE — REQUIRES UPDATE** | Reconcile to zero-Redis architectural decision |
| **Multi-Agent AI** | `DOC-AI-001` | Single LLM Gateway + Deterministic FSM | **HISTORICAL / FUTURE** | Retain as future horizon |

---

### 7. CORRECT TEST TERMINOLOGY & METRICS

- **Test Cases Passed**: **85 total passing test cases** (0 failures, 0 errors, 0 skipped).
  - Main application test suite: **78 passing test cases** (`pytest tests/ -v`).
  - Sprint 0 baseline regression suite: **7 passing test cases** (`pytest spikes/test_sprint0_suite.py -v`).
- **Assertions Evaluated**: ~240 individual Python `assert` statements evaluated across the 85 test cases.

---

### 8. ANALYTICS STORAGE DECISION ANALYSIS

Comparing storage options for operational event telemetry:

- **Option A (Recommended for MVP)**: **Structured Application Log Stream (stdout/application log file)**.
  - Anonymous JSON events written to application log stream via Python `logging`. Incurs **₹0 cost**, requires **zero database write overhead**, and **zero third-party tracking scripts**.
- **Option B**: SQL Server Telemetry Table (`dbo.telemetry_events`). *Cons*: Adds write bloat to database.
- **Option C**: Plausible / PostHog SaaS. *Cons*: External script dependency, potential privacy friction.

---

### 9. SECURITY TEST COVERAGE MATRIX

| Security Control | Implementation Vector | Existing Test Case | Phase 6 Missing Test |
| :--- | :--- | :--- | :--- |
| **SQL Injection Defense** | SQLAlchemy 2.x ORM Parameterization | `test_models.py` | Add raw T-SQL attack payload test |
| **XSS Defense** | Jinja2 Global Auto-escaping | `test_frontend.py` | Add `<script>` payload injection test in form fields |
| **PII Sanitization** | `scrub_pii()` regex scrubber | `test_ai_gateway.py` | Add API key, credit card, SSN redaction tests |
| **CSRF Defense** | `SameSite=Lax` cookies | `test_discovery_ux.py` | Add explicit CSRF token header validation test |
| **Security Headers** | Security Headers Middleware | Missing | Add test asserting `X-Frame-Options` & `CSP` headers |
| **Rate Limiting** | Native In-Memory Rate Limiter | Missing | Add test asserting HTTP 429 when POST > 5 req/min |
| **State Machine Guard**| Discovery FSM `is_unlocked` guard | `test_fsm.py` | Retain 9 state transition tests |
| **AI Fallback Circuit** | Provider-Neutral Gateway Timeout | `test_ai_gateway.py` | Add circuit breaker fallback state test |

---

### 10. DEPENDENCY & COST IMPACT

- **Required Additions**: `Bandit` (Static Python security linter, **₹0**).
- **Zero-Cost Tooling**: GitHub Actions free tier, native FastAPI middleware, structured application log file.
- **Zero New Dependencies**: No npm packages, no Node build tools, no Redis, no external SaaS dependencies required for MVP.

---

### 11. OWNER DECISIONS STILL REQUIRED

1. **Production Hosting Platform**: Candidate Option A (Azure App Service + Azure SQL) vs Option B (Linux VPS + SQL Container) vs Option C (AWS).
2. **Telemetry & Analytics Storage**: Option A (Structured stdout/log file at **₹0 cost**, Recommended) vs Option B (Plausible $9/mo).
3. **E2E Testing Toolchain**: Option A (Retain Pytest + FastAPI `TestClient` at **sub-second speed, ₹0 bloat**, Recommended) vs Option B (Playwright Node E2E).

---

### 12. CORRECTED IMPLEMENTATION SEQUENCE

```
Phase 6.1 (Security Hardening) ──► Phase 6.2 (Testing Expansion) ──► Phase 6.3 (Performance & Reliability)
                                                                           │
Phase 6.5 (Telemetry & Analytics) ◄── Phase 6.4 (DevOps & CI/CD) ──────────┘
```

1. **Phase 6.1 — Security Hardening**:
   - Implement Security Headers Middleware (`X-Frame-Options`, `nosniff`, `CSP`).
   - Implement Native In-Memory Rate Limiting on public POST endpoints (`/contact`, `/discovery/problem`, `/discovery/unlock`, `/discovery/review`).
   - Expand PII regex scrubber catalog (`scrub_pii()`).
2. **Phase 6.2 — Testing Expansion**:
   - Add security header assertions, rate limit tests, malformed payload tests, and circuit breaker fallback tests.
3. **Phase 6.3 — Performance & Reliability**:
   - Add static asset Cache-Control header middleware and slow-query logging probes (>500ms).
4. **Phase 6.4 — DevOps & CI/CD**:
   - Create `.github/workflows/ci.yml` running SQL Server Linux container, Bandit security scans, and 85+ test assertions.
5. **Phase 6.5 — Telemetry & Analytics**:
   - Implement custom zero-cost FastAPI telemetry middleware logging anonymous event taxonomy.

---

### HARD STOP

**Final status:**  
`PHASE 6 PLANNING CORRECTED — AWAITING OWNER APPROVAL`
