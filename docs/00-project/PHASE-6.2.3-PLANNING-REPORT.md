# Phase 6.2.3 — Observability, Analytics & Application Telemetry
## Comprehensive Planning & Architecture Report

**Document ID:** `DOC-REP-6.2.3-001`  
**Phase:** Phase 6.2.3 (Observability, Product Analytics & Telemetry Strategy)  
**Status:** PHASE 6.2.3 PLANNING COMPLETE — AWAITING OWNER APPROVAL  
**Date:** 2026-09-18  
**Architecture Preserved:** Python 3.13 · FastAPI · Uvicorn · Jinja2 · HTMX · Alpine.js · SQLAlchemy 2.x · Alembic · Microsoft SQL Server 2022 · pyodbc · Modular Monolith  

---

## 1. Executive Summary

Phase 6.2.2 established verified static analysis and code quality gates (Ruff, Bandit, pip-audit) alongside the automated GitHub Actions CI pipeline running 92/92 regression tests against real Microsoft SQL Server 2022 containers. 

This planning report defines the architectural strategy for **Phase 6.2.3: Observability, Analytics & Application Telemetry**.

The core objective of Phase 6.2.3 is to establish comprehensive visibility into:
1. **Application Health & Runtime Behavior:** Request rates, HTTP status codes, latencies, and uptime.
2. **Error & Failure Diagnostics:** Unhandled exceptions, validation rejections, database connectivity drops, and AI Gateway timeouts.
3. **Performance Signals:** Slow request execution and slow SQL Server queries.
4. **Discovery Funnel Progression:** Anonymous, privacy-preserving conversion and drop-off tracking across the 7 user-facing consultative discovery stages.
5. **Security & Abuse Monitoring:** Rate-limit violations, suspicious client behavior, and unauthorized resource access attempts.
6. **Correlation Across System Boundaries:** Distributed tracing across middleware, route handlers, background tasks, and database queries.

In strict alignment with foundational project constraints (`BD-001`, `BD-015`, `CST-CNF-008`), this observability framework will be delivered with:
- **Zero Third-Party Client Tracking Scripts** (no Google Analytics, Meta Pixel, PostHog, or Plausible scripts injected into frontend templates).
- **Zero Database Write Bloat** (telemetry events are NOT written to Microsoft SQL Server tables, preserving database I/O exclusively for business leads, sessions, and artifacts).
- **Zero New Infrastructure or Daemons** (no Redis, no Kafka, no Elasticsearch, no Prometheus/Grafana servers, no APM agents).
- **Zero New Runtime Dependencies** (100% standard library `logging`, `contextvars`, `json`, and existing FastAPI/SQLAlchemy primitives).
- **₹0 Infrastructure Cost** for local development and CI execution.

---

## 2. Authoritative Baseline

The system architecture and verified operational baseline are defined as follows:

| Dimension | Authoritative Specification | Implementation Reference |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.13.15 64-bit | `pyproject.toml`, `.github/workflows/ci.yml` |
| **Web Framework** | FastAPI 0.115.x + Uvicorn 0.34.x (ASGI) | `app/main.py` |
| **Frontend Stack** | Jinja2 + HTMX 1.9.10 + Alpine.js 3.13.5 + Vanilla CSS tokens | `templates/`, `static/vendor/` |
| **Persistence Engine** | Microsoft SQL Server 2022 Developer/Express (Local) / Linux Container (CI) | `mcr.microsoft.com/mssql/server:2022-latest` |
| **Driver & Bridge** | Microsoft ODBC Driver 18 for SQL Server + `pyodbc` 5.2.x | `app/database/connection.py` |
| **ORM & Migrations** | SQLAlchemy 2.0.x + Alembic (Head: `4941998763bd`) | `app/database/models.py`, `migrations/` |
| **Architecture Style** | Modular Monolith with bounded domains (`discovery`, `blueprint`, `opportunity`, `estimation`, `leads`, `review`) | `app/modules/` |
| **Test Suite Baseline** | **92 / 92 Passed (100%)**: 85 Application Tests + 7 Sprint 0 Regression Tests | CI Run ID `35259665104` |
| **Code Quality Baseline** | Ruff: 0 errors; Bandit: 0 security findings; pip-audit: 0 vulnerabilities | CI Run ID `35259665104` |

---

## 3. Existing Observability Audit

A comprehensive audit of the active codebase was performed to distinguish what is already implemented, what is partially implemented, what is missing, and what is proposed for Phase 6.2.3:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                OBSERVABILITY MATURITY MATRIX                             │
├──────────────────────────┬───────────────────────────────────────┬───────────────────────┤
│ Component                │ Current Codebase Status               │ Phase 6.2.3 Status    │
├──────────────────────────┼───────────────────────────────────────┼───────────────────────┤
│ Root Logging System      │ Implemented (Console & JSONFormatter) │ Enrich & Standardize  │
│ Sensitive Key Redaction  │ Partially Implemented (Regex Filter)  │ Expand to PII/Headers │
│ Request Correlation ID   │ Implemented (ContextVar + Middleware) │ Preserve & Propagate  │
│ Request Duration Timing  │ Partially Implemented (Debug-only log)│ Elevate to Structured │
│ Exception Envelopes      │ Implemented (DOC-ARCH-008 Envelopes)  │ Preserve & Correlate  │
│ Rate-Limit Telemetry     │ Partially Implemented (Logs raw IP)   │ Anonymize (hash_ip)   │
│ DB Session Error Logging │ Implemented (Rollback warnings)       │ Preserve              │
│ Slow Query Detection     │ Missing                               │ Implement (SQLAlchemy)│
│ AI Gateway Observability │ Partially Implemented (Plain text log)│ Add Structured Events │
│ Health & Readiness Probe │ Implemented (/health/live & /ready)   │ Exclude from Analytics│
│ Anonymous Funnel Events  │ Missing                               │ Implement (In-House)  │
│ Static Asset Noise Gate  │ Missing                               │ Filter from Logs      │
│ PII Sanitization in Logs │ Partially Leaking (web.py:283)        │ Remediate Immediately │
└──────────────────────────┴───────────────────────────────────────┴───────────────────────┘
```

### Detailed Component Audit

#### A. Already Implemented
1. **Core Logging Infrastructure (`app/shared/logging.py`):**
   - `configure_logging(level, json_format)` mounts a stream handler to `sys.stdout`.
   - `SensitiveFilter` intercepts log records and redacts common connection string passwords (`pwd=`, `password=`).
   - `JSONLogFormatter` serializes log records to single-line JSON (`timestamp`, `level`, `logger`, `correlation_id`, `message`, `exception`).
   - Custom log record factory injects `correlation_id` from ContextVar into standard human-readable formatter.
2. **Correlation ID Lifecycle (`app/main.py`):**
   - `correlation_id_middleware` extracts incoming `X-Correlation-ID` or `X-Request-ID` headers or generates a fresh `uuid.uuid4()`.
   - Stores ID in `correlation_id_ctx: ContextVar[str]` and attaches `X-Correlation-ID` to all outbound HTTP responses.
3. **Standard Error Envelopes (`app/shared/exceptions.py`):**
   - Implements DOC-ARCH-008 canonical error envelope (`success: False`, `error: {code, message, details}`, `meta: {request_id, timestamp}`).
   - Handlers in `app/main.py` handle `AppException`, `RequestValidationError`, `StarletteHTTPException`, and generic `Exception`.
4. **Health & Readiness Endpoints (`app/routers/health.py`):**
   - `GET /health/live`: Process uptime and liveness.
   - `GET /health/ready`: Live empirical `SELECT 1` ping against Microsoft SQL Server with query latency.

#### B. Partially Implemented
1. **Request Completion Logging (`app/main.py`):**
   - In `correlation_id_middleware`:
     ```python
     duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
     logger.debug(f"{request.method} {request.url.path} completed in {duration_ms}ms")
     ```
   - *Limitation:* Emitted only at `DEBUG` level (suppressed in production where `debug=False`). Does not capture HTTP status code, query parameters, or client classification.
2. **Rate Limit Security Logging (`app/main.py`):**
   - Logs `logger.warning(f"Rate limit exceeded for IP {client_ip} on path {request.url.path}")`.
   - *Limitation:* Logs raw client IP address (violating data minimization). `request_id` passed to `format_error_response` is currently empty string `""`.
3. **AI Gateway Fallback Logging (`app/ai_gateway/gateway.py`):**
   - Logs timeouts, schema validation failures, and provider errors as plain text strings.
   - *Limitation:* Unstructured; does not emit machine-readable telemetry on fallback engagement.
4. **Contact Submission Logging (`app/routers/web.py`):**
   - *Critical Audit Finding:* Line 283 logs `corporate_email` in plain text to stdout:
     ```python
     logger.info(f"Inquiry received from {sanitized_name} ({corporate_email}) | ...")
     ```
   - *Limitation:* Direct violation of zero-PII logging mandate.

#### C. Missing
1. **In-House Anonymous Product Telemetry Emitter:** No structured mechanism to emit funnel conversion events (`discovery_started`, `discovery_stage_completed`, `opportunity_map_viewed`, `blueprint_unlocked`, etc.).
2. **Database Query Latency & Slow Query Probe:** No instrumentation hook on SQLAlchemy engine to identify SQL queries exceeding acceptable thresholds (>500ms).
3. **Log Noise Filtering:** High-frequency container health probes (`/health/live`, `/health/ready`) and static asset fetches (`/static/*`) generate log noise without telemetry suppression rules.
4. **Structured JSON Telemetry Schema:** `JSONLogFormatter` does not merge arbitrary `extra={...}` dictionary properties into the JSON envelope.

#### D. Proposed for Phase 6.2.3
1. Unified `emit_telemetry_event(...)` module with strict event name validation and automatic PII dropping.
2. Enhanced `JSONLogFormatter` that merges structured event payloads into top-level JSON fields.
3. Native SQLAlchemy Core `before_cursor_execute` and `after_cursor_execute` event listeners for slow query detection.
4. Production request completion access log at `INFO` with duration, method, path, and status code.
5. PII leak remediation in `app/routers/web.py`.
6. Telemetry noise filtering for health endpoints and static files.

---

## 4. Logging Architecture

The logging architecture must balance developer ergonomics during local engineering with machine-readable operational parsing in production.

### 4.1 Dual-Mode Formatting Strategy

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               DUAL-MODE LOGGING STRATEGY                               │
├──────────────────────────────────────────┬─────────────────────────────────────────────┤
│ Development / Local (app_env != prod)   │ Production (app_env == "production")        │
├──────────────────────────────────────────┼─────────────────────────────────────────────┤
│ Format: Human-readable ANSI color console│ Format: Single-line NDJSON to stdout        │
│ Destination: sys.stdout                  │ Destination: sys.stdout                     │
│ Level: DEBUG (if debug=True) else INFO   │ Level: INFO                                 │
│ Structure: Timestamp, Level, Logger,     │ Structure: Machine-readable JSON object     │
│ [corr:id], Message, formatted context    │ with standardized key-value schema          │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
```

### 4.2 Production NDJSON Schema Specification

Every log line emitted in production will be a single-line valid JSON object conforming to the following schema:

```json
{
  "timestamp": "2026-09-18T00:15:30.123456Z",
  "level": "info",
  "logger": "app.modules.discovery.service",
  "correlation_id": "9e0a3c4d-59a5-4fe2-b711-ff3fcfe4f430",
  "event": "discovery_started",
  "message": "Initialized new discovery session 42",
  "context": {
    "entry_point": "homepage_hero",
    "session_token_hash": "a1b2c3d4e5f6...",
    "stage": "START"
  },
  "duration_ms": null,
  "http": {
    "method": "POST",
    "path": "/discovery/start",
    "status_code": 201
  }
}
```

### 4.3 Mandatory Redaction & Anti-PII Filter

Logging filters will enforce redaction across two levels:
1. **`SensitiveFilter` (Global Log Handler):**
   - Automatically masks any string matching sensitive patterns:
     - `pwd=[^;]+` $\rightarrow$ `pwd=[REDACTED]`
     - `password=[^;]+` $\rightarrow$ `password=[REDACTED]`
     - `Bearer [A-Za-z0-9_\-\.]+` $\rightarrow$ `Bearer [REDACTED]`
     - `sk-[A-Za-z0-9]{20,}` $\rightarrow$ `[REDACTED_API_KEY]`
     - Email patterns $\rightarrow$ `[REDACTED_EMAIL]`
2. **Pre-Emission Sanitization:**
   - Handlers must call `scrub_pii()` from `app/shared/security.py` on any unstructured text or user input before composing log records.
   - Raw user problem statements, corporate emails, user names, and credit card numbers are strictly prohibited from log strings.

---

## 5. Correlation & Request Telemetry

Request correlation is foundational to tracing an interaction from frontend dispatch to database execution.

### 5.1 Correlation Propagation Mechanics

1. **Incoming Request Extraction:**
   - Look for `X-Correlation-ID` header.
   - Fall back to `X-Request-ID` header.
   - Fall back to generating a cryptographically random UUIDv4 string.
2. **Context Binding:**
   - Store in `correlation_id_ctx: ContextVar[str]` for threadpool and async safety.
3. **Outbound Response:**
   - Always inject `X-Correlation-ID` into HTTP response headers.
4. **Error Correlation:**
   - Inject the active correlation ID into `meta.request_id` in all DOC-ARCH-008 error responses.

### 5.2 Request Completion Access Telemetry

The outermost `correlation_id_middleware` will be updated to record request execution metrics:
- **HTTP Method** (`GET`, `POST`, etc.)
- **Route Path** (e.g. `/discovery/problem`)
- **HTTP Status Code** (e.g. `200`, `422`, `500`)
- **Duration in Milliseconds** (calculated via `time.perf_counter()`)
- **Client IP Classification** (hashed via `hash_ip()` or masked as `xxx.xxx.xxx.0/24`)

### 5.3 Noise Suppression Gates

To prevent operational log saturation:
- **Health Probes (`/health/live`, `/health/ready`):** Logged at `DEBUG` level only. Never emit product analytics events.
- **Static Assets (`/static/*`, `/favicon.ico`):** Logged at `DEBUG` level only.
- **Log Volume Budget:** Standard user discovery journeys produce ~10-15 structured log lines total across all 7 stages.

---

## 6. Performance Observability

Performance telemetry identifies execution bottlenecks without requiring heavy Application Performance Monitoring (APM) agents or external SaaS daemons.

### 6.1 Application Request Latency Thresholds

| Metric | Target (P95) | Slow Warning Threshold | Action on Exceeded |
| :--- | :---: | :---: | :--- |
| **Static / Web Pages** | $< 50\text{ ms}$ | $> 500\text{ ms}$ | Log `event="slow_http_request"` warning with path and duration |
| **Discovery API / HTMX** | $< 150\text{ ms}$ | $> 1,000\text{ ms}$ | Log `event="slow_http_request"` warning with stage and duration |
| **AI Gateway Operations** | $< 3,000\text{ ms}$ | $> 8,000\text{ ms}$ | Log `event="slow_ai_request"` warning with model and duration |

### 6.2 Database Query Latency & Slow Query Probe

In previous planning (`PHASE-6.2-PLANNING-REPORT.md`), a slow-query threshold was discussed:
- **SQL Slow-Query Threshold:** $> 500\text{ ms}$

#### Implementation Mechanics (Native SQLAlchemy Core Events)
Using SQLAlchemy 2.x event listeners attached to the engine singleton in `app/database/connection.py`:
```python
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time_ms = (time.perf_counter() - context._query_start_time) * 1000
    if total_time_ms > settings.slow_query_threshold_ms:
        logger.warning(
            f"Slow SQL query detected ({total_time_ms:.2f}ms)",
            extra={
                "event": "slow_sql_query",
                "duration_ms": round(total_time_ms, 2),
                "statement": statement[:300],  # Truncated query preview
            }
        )
```
- **Zero Third-Party Packages:** Utilizes built-in SQLAlchemy Core events.
- **Zero Overhead:** Negligible nanosecond timestamp delta on execution.
- **Owner Approval Required:** The $> 500\text{ ms}$ threshold is submitted for formal owner confirmation.

---

## 7. Error & Failure Observability

The system must capture sufficient diagnostic context to troubleshoot failures rapidly while strictly preventing information leakage to public users.

### 7.1 Failure Classification & Observability Matrix

| Failure Type | HTTP Status | Log Level | Emitted Log Attributes | User Envelope Message |
| :--- | :---: | :---: | :--- | :--- |
| **Validation Error** | 422 | `INFO` / `WARN` | `field`, `validation_rule`, `correlation_id` | Specific parameter validation failure details |
| **Rate Limit Exceeded** | 429 | `WARN` | `event="rate_limit_exceeded"`, `path`, `ip_hash` | Standard rate limit notice (5 req/min, retry-after: 60) |
| **Entity Not Found** | 404 | `INFO` | `entity_name`, `entity_id`, `correlation_id` | Standard not found message |
| **Access Forbidden** | 403 | `WARN` | `event="forbidden_access"`, `resource`, `session_token_hash` | Gated asset notice (e.g. Blueprint locked) |
| **AI Gateway Timeout** | 502 / Fallback | `WARN` | `event="ai_fallback"`, `reason="TIMEOUT"`, `duration_ms` | Seamless heuristic delivery (no error shown to user) |
| **AI Schema Mismatch** | 502 / Fallback | `WARN` | `event="ai_fallback"`, `reason="SCHEMA_ERROR"` | Seamless heuristic delivery (no error shown to user) |
| **Database Failure** | 503 | `ERROR` | `error_type`, `db_operation`, `correlation_id`, `exc_info` | "A database error occurred. Details suppressed for security." |
| **Unhandled Exception**| 500 | `ERROR` | Full Python traceback (`exc_info=True`), `correlation_id` | "An unexpected internal server error occurred." |

### 7.2 Security Safeguards on Errors
- **Zero Stack Traces in HTTP Responses:** Unhandled exceptions emit full tracebacks to stdout logs only. The client receives strictly `code="INTERNAL_SERVER_ERROR"` with `request_id`.
- **Zero Database Schema or Connection Details:** Database errors suppress connection strings and SQL syntax details from client responses.

---

## 8. Anonymous Product Analytics

### 8.1 In-House Architecture Evaluation
Authoritative specification `docs/18-analytics/01-ANALYTICS-SPECIFICATION.md` mandates **Option A (Structured Application Log Stream)**:
- **No Third-Party Analytics SaaS:** Zero Google Analytics, PostHog, or Plausible accounts required for MVP.
- **No Analytics Database:** Telemetry events are NOT written to Microsoft SQL Server tables (preserves database performance and avoids write contention).
- **Server-Side Emission:** Emitted directly within FastAPI route handlers and coordinator services upon successful domain actions. 100% verified, ad-blocker immune, zero client network overhead.

### 8.2 Canonical Event Taxonomy (7 Core Funnel Events)

The seven canonical telemetry events remain the approved telemetry taxonomy, and their proposed trigger points are mapped to the current discovery UX/FSM. Exact implementation trigger placement must be verified against the current route/template lifecycle during implementation:

| # | Event Name | Trigger Condition | Code Location | Payload Context (Strictly Anonymous) | PII Prohibited |
| :-: | :--- | :--- | :--- | :--- | :---: |
| **1** | `discovery_started` | User initializes discovery session | `app/modules/discovery/service.py:start_session` | `session_token_hash`, `entry_point`, `timestamp` | YES |
| **2** | `discovery_stage_completed` | User advances across any of the 7 stages | `app/modules/discovery/service.py:submit_*` | `session_token_hash`, `stage_number`, `stage_name`, `dwell_time_sec` | YES |
| **3** | `opportunity_map_viewed` | Stage 4 synthesis rendered | `app/modules/discovery/service.py:get_opportunity_map` | `session_token_hash`, `opportunity_count`, `complexity_tier` | YES |
| **4** | `blueprint_unlock_started` | User triggers lead capture unlock modal | `app/routers/discovery_views.py:discovery_unlock_view` | `session_token_hash`, `trigger_source` | YES |
| **5** | `blueprint_unlocked` | User successfully submits lead & unlocks | `app/modules/discovery/service.py:unlock_with_lead` | `session_token_hash`, `timestamp` *(Name & email sent to `dbo.leads` only, NEVER to telemetry)* | YES |
| **6** | `estimate_viewed` | Stage 6 indicative estimate rendered | `app/modules/discovery/service.py:get_blueprint` | `session_token_hash`, `complexity_tier`, `currency` | YES |
| **7** | `contact_submitted` | User submits contact form inquiry | `app/routers/web.py:contact_submit` | `project_scope_category`, `has_company`, `timestamp` *(Name & email sent to DB/alert only)* | YES |

---

## 9. Privacy & Data Minimization

Telemetry and observability implementations must comply with core data minimization principles:

1. **Purpose Limitation:** Telemetry is captured solely to monitor application health, detect system errors, identify slow performance, and understand aggregate funnel drop-off.
2. **Data Minimization:** Only the minimum necessary identifiers (e.g. SHA-256 session token hashes) are logged.
3. **Strictly Prohibited Data in Telemetry Stream:**
   - ✕ User full names, email addresses, phone numbers
   - ✕ Raw user problem statement text (may contain proprietary business information)
   - ✕ AI prompts and LLM completion outputs
   - ✕ Financial figures, proprietary budgets, or custom contract terms
   - ✕ Cryptographic secrets, HMAC keys, database passwords, session tokens
   - ✕ Raw client IP addresses (must be hashed or masked)
4. **No Unsupported Legal Claims:** The documentation will not fabricate compliance claims (e.g., claiming formal "SOC 2 Type II certification", "HIPAA compliance", or "ISO 27001 certification"). The implementation represents privacy-by-design engineering.

---

## 10. Retention

Retention governance must clearly distinguish between persistent business data and ephemeral operational logs:

1. **Persistent Business Data (SQL Server):**
   - Active leads and consultation requests are governed by business lifecycle requirements.
   - Anonymous inactive discovery sessions: `session_max_age_seconds = 2592000` (30 days TTL), after which sessions expire.
2. **Operational Log & Telemetry Retention:**
   - **Local Development / CI:** Ephemeral; logs terminate with process shutdown or CI container disposal.
   - **Production Deployment:** Production log retention remains provider-dependent. No fixed production retention period is approved at MVP planning stage.

---

## 11. Security Events

Minimal security events will be emitted as structured telemetry without the complexity of a heavy SIEM platform:

| Security Event | Trigger Condition | Emitted Attributes | Log Severity |
| :--- | :--- | :--- | :---: |
| `rate_limit_exceeded` | Client exceeds 5 requests / 60 seconds on sensitive POST routes | `event="rate_limit_exceeded"`, `route`, `ip_hash` | `WARNING` |
| `invalid_session_cookie` | Cryptographic HMAC verification fails on session cookie | `event="invalid_cookie"`, `reason`, `ip_hash` | `WARNING` |
| `unauthorized_blueprint_access`| Client attempts to access locked blueprint (`403`) | `event="blueprint_locked_access"`, `session_token_hash` | `WARNING` |
| `repeated_validation_failure` | Client sends $>3$ malformed payloads in succession | `event="repeated_validation_error"`, `route`, `ip_hash` | `WARNING` |
| `database_connection_loss` | Engine fails readiness probe or pool checkout | `event="db_connection_lost"`, `error_class` | `ERROR` |

---

## 12. Database Observability

Visibility into Microsoft SQL Server 2022 connection and query behavior:

1. **Connection Pool Visibility:**
   - Monitored pool settings: `pool_size` (10), `max_overflow` (20), `pool_recycle` (1800s), `pool_pre_ping=True`.
   - Engine lifecycle events logged during application lifespan (`Booting ...`, `Disposing SQL Server connection pool`).
2. **Transaction Integrity:**
   - `app/database/session.py` catches all exceptions, executes `db.rollback()`, and logs warnings.
3. **Slow Query Tracking:**
   - Track execution duration of all queries via SQLAlchemy event hooks without schema modifications.
4. **Architectural Guardrails:**
   - **No schema changes.**
   - **No new analytics tables in SQL Server.**
   - **No Redis cache layer.**

---

## 13. AI Gateway Observability

The AI Gateway orchestrator (`app/ai_gateway/gateway.py`) is provider-neutral and coordinates model execution with deterministic fallback catalogs:

### 13.1 Observable AI Signals
1. **`ai_request_initiated`:** Model identifier, operation (`clarifications` vs `opportunity_map`), sanitized character count.
2. **`ai_request_completed`:** Duration in milliseconds, model identifier, provider status (`PROVIDER_LLM`).
3. **`ai_fallback_engaged`:** Duration in milliseconds, trigger reason (`FALLBACK_TIMEOUT`, `FALLBACK_SCHEMA_ERROR`, `FALLBACK_PROVIDER_ERROR`).

### 13.2 Privacy Safeguards
- Raw user problem text is scrubbed before processing.
- Prompts, raw completions, and clarification text are **NEVER** serialized into telemetry logs.
- Gateway maintains provider-neutrality; zero vendor-specific SDK telemetry.

---

## 14. Dashboard / Reporting Evaluation

| Criteria | Option A: Structured Logs Only (stdout / NDJSON) | Option B: Local Log Inspection CLI (`scripts/inspect_telemetry.py`) | Option C: SQL Server Analytics Table + Admin UI | Option D: Third-Party SaaS (Plausible / PostHog) |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture** | **Zero infrastructure** | Tiny standalone script | New DB tables + admin routes | External tracking script + SaaS |
| **Cost** | **₹0 / $0** | **₹0 / $0** | ₹0 (local), higher DB storage | $0 to $20+/month |
| **Privacy Posture** | **100% In-House / Zero PII** | **100% Local / In-House** | In-house DB persistence | Data transmitted externally |
| **Database I/O** | **Zero DB overhead** | **Zero DB overhead** | Adds write contention | Zero DB overhead |
| **Maintenance** | **Zero maintenance** | Minimal maintenance | High (migrations, UI maintenance)| Vendor dependency |
| **Complexity** | **Lowest** | Low | High | Medium |
| **MVP Fit** | **Recommended Baseline** | **Recommended Developer Tool** | **Rejected for MVP** | **Rejected for MVP** |

### Recommendation
1. Implement **Option A** as the primary production telemetry architecture.
2. Implement **Option B** as a lightweight, optional developer script for local funnel analysis.
3. **Reject Option C** (adds database write overhead and unnecessary admin surface).
4. **Reject Option D** (violates privacy-by-design and introduces external SaaS costs).

---

## 15. Testing Strategy for Phase 6.2.3

Phase 6.2.3 implementation will introduce a dedicated, automated test suite (`tests/test_observability.py`) covering all telemetry, logging, and security behaviors:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                               PHASE 6.2.3 TEST SPECIFICATION                             │
├────────────────────────────────┬─────────────────────────────────────────────────────────┤
│ Test Identifier                │ Verification Objective                                  │
├────────────────────────────────┼─────────────────────────────────────────────────────────┤
│ `test_json_formatter_schema`   │ Verify JSONFormatter outputs valid NDJSON with all keys │
│ `test_correlation_propagation` │ Verify X-Correlation-ID propagates to response & logs   │
│ `test_sensitive_data_redacted` │ Verify passwords, connection strings, and tokens masked │
│ `test_contact_log_pii_scrubbed`│ Verify contact submission does NOT leak email to stdout │
│ `test_telemetry_event_emitter` │ Verify emit_telemetry_event produces valid event schema │
│ `test_telemetry_taxonomy_gate` │ Verify unapproved event names are rejected/dropped      │
│ `test_telemetry_pii_exclusion` │ Verify customer names/emails are rejected from payload  │
│ `test_slow_request_logging`    │ Verify requests exceeding threshold log warning event   │
│ `test_health_probe_exclusion`  │ Verify /health/live and /ready do NOT emit analytics    │
│ `test_static_asset_exclusion`  │ Verify /static/* requests do NOT pollute access logs    │
│ `test_slow_sql_query_listener` │ Verify queries exceeding 500ms trigger slow_sql_query   │
│ `test_rate_limit_telemetry`    │ Verify 429 response emits rate_limit_exceeded with hash │
│ `test_ai_gateway_telemetry`    │ Verify AI fallback emits structured telemetry event     │
│ `test_error_envelope_corr_id`  │ Verify 404, 422, and 500 envelopes contain request_id   │
└────────────────────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 16. Dependency & Infrastructure Governance

- **Runtime Dependencies:** **ZERO new packages added to `requirements.txt`.**
  - Standard library `logging`, `contextvars`, `json`, `re`, `hashlib`, and `time` completely satisfy all requirements.
  - Existing `FastAPI`, `Starlette`, and `SQLAlchemy` provide all needed middleware and event hooks.
- **Development Dependencies:** **ZERO new packages.** Ruff, Bandit, and pip-audit configured in Phase 6.2.2 remain the complete toolset.
- **External Services:** **ZERO external services.** No Redis, no external SaaS, no cloud telemetry endpoints.

---

## 17. Cost Governance

| Environment | Cost | Justification |
| :--- | :---: | :--- |
| **Local Development** | **₹0 / $0** | Stdlib logging to console/stdout + local SQL Server 2022 Express. |
| **GitHub Actions CI** | **₹0 / $0** | Executes within free runner tier; SQL Server container runs in CI service. |
| **Future Production Hosting** | **Provider-Dependent** | Stdlib logging writes to stdout; host log collection (systemd journald, container stdout) incurs no incremental licensing fees. |

*Governance Assertion:* MVP observability satisfies the strict ₹0 infrastructure goal without making speculative guarantees about high-scale third-party production infrastructure.

---

## 18. Documentation Drift Audit

A thorough lexical and architectural scan was conducted across the documentation repository. The findings are categorized below:

### Category A: Active & Authoritative
- `docs/18-analytics/01-ANALYTICS-SPECIFICATION.md`: Authoritative specification selecting Option A (Structured Log Stream) and rejecting PostHog/Google Analytics.
- `docs/00-project/PHASE-6.2-PLANNING-REPORT.md`: Section 8 defines the 7-event taxonomy and zero-database telemetry model.
- `docs/00-project/PHASE-6.2.1-IMPLEMENTATION-REPORT.md` & `PHASE-6.2.2-IMPLEMENTATION-REPORT.md`: Verified baselines for CI and static analysis gates.

### Category B: Historical Documentation (Superseded but Legitimate Record)
- `docs/00-project/PYTHON_FIRST_ARCHITECTURE_EVALUATION.md`: Historical evaluation document predating the final Python-first decision (`BD-015`).
- `docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md` (`ADR-001`, `ADR-002`): Architectural records documenting the rejection of React/Next.js and PostgreSQL.

### Category C: Stale References (Requires Future Reconciliation)
1. **Redis / Celery References:**
   - `docs/04-website/14-SEO-CONTENT-ROADMAP.md` (line 49): References "background worker queues (Redis/Celery)".
   - `docs/04-website/07-UX-WIREFRAME-SPEC.md` (line 214): Mentions "Background Queue (Celery/Redis)".
   - `docs/00-project/DOCUMENTATION_ARCHITECTURE.md` (line 136): References "Upstash Redis".
2. **Next.js / React References:**
   - `docs/00-project/PROJECT_GLOSSARY.md` (line 51): Defines "App Router Next.js 15".
   - `docs/00-project/DEPENDENCY_GRAPH.md` (line 57): References "Next.js App Router".
   - `docs/00-project/DOCUMENTATION_ARCHITECTURE.md` (lines 113, 119): References Next.js 15.
3. **Analytics SaaS References:**
   - `docs/04-website/18-WEBSITE-OPEN-QUESTIONS.md` (`WOQ-005`): Mentions vendor selection (Plausible vs PostHog). Superseded by `DOC-ANA-001`.
   - `docs/01-business/CLIENT_JOURNEY.md` (line 162) & `AI_NATIVE_OPERATING_MODEL.md` (line 76): References analyzing PostHog logs. Superseded by structured log streams.
4. **Old Discovery Endpoints:**
   - `docs/05-architecture/08-API-ARCHITECTURE.md` (line 110): References `/api/v1/discovery-sessions/problem` (plural noun); implemented route is `/api/v1/discovery/problem`.
   - `docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md` (line 49): References `POST /api/v1/discovery/ingest`.

*Note: In accordance with planning instructions, zero documentation files will be modified during this planning phase.*

---

## 19. Proposed File Changes (Phase 6.2.3 Implementation Scope)

When Phase 6.2.3 implementation is authorized, the following precise changes will be made:

| File Path | Action | Purpose & Expected Behavior | Dependencies | Tests Affected |
| :--- | :---: | :--- | :--- | :--- |
| [`app/config.py`](file:///d:/Project_website/app/config.py) | **MODIFY** | Add `log_format: Literal["text", "json"] = "text"`, `slow_query_threshold_ms: float = 500.0`, and `slow_request_threshold_ms: float = 1000.0` configuration fields. | None | `test_config.py` |
| [`app/shared/logging.py`](file:///d:/Project_website/app/shared/logging.py) | **MODIFY** | Enhance `JSONLogFormatter` to merge `event`, `duration_ms`, `http`, and `context` fields into JSON output; expand `SensitiveFilter` regexes. | None | `test_observability.py` |
| [`app/shared/telemetry.py`](file:///d:/Project_website/app/shared/telemetry.py) | **NEW** | Author lightweight in-house telemetry emitter: `emit_telemetry_event(event_name, payload)`. Validates event taxonomy, scrubs PII, logs to `app.telemetry`. | None | `test_observability.py` |
| [`app/main.py`](file:///d:/Project_website/app/main.py) | **MODIFY** | Update `correlation_id_middleware` to emit request completion log with duration & status code; filter health/static noise; hash IP in rate limiter warning. | None | `test_observability.py` |
| [`app/database/connection.py`](file:///d:/Project_website/app/database/connection.py) | **MODIFY** | Register SQLAlchemy Core `before_cursor_execute` and `after_cursor_execute` hooks to detect and log queries exceeding `slow_query_threshold_ms`. | None | `test_database.py`, `test_observability.py` |
| [`app/ai_gateway/gateway.py`](file:///d:/Project_website/app/ai_gateway/gateway.py) | **MODIFY** | Emit structured `ai_completion` and `ai_fallback` events via `emit_telemetry_event` with duration and source flag (zero raw prompts). | None | `test_ai_gateway.py` |
| [`app/modules/discovery/service.py`](file:///d:/Project_website/app/modules/discovery/service.py) | **MODIFY** | Instrument 6 discovery funnel events (`discovery_started`, `discovery_stage_completed`, `opportunity_map_viewed`, `blueprint_unlock_started`, `blueprint_unlocked`, `estimate_viewed`). | None | `test_discovery_service.py` |
| [`app/routers/web.py`](file:///d:/Project_website/app/routers/web.py) | **MODIFY** | Remediate line 283 PII leak; emit `contact_submitted` event with sanitized non-PII payload. | None | `test_public_website.py` |
| [`scripts/inspect_telemetry.py`](file:///d:/Project_website/scripts/inspect_telemetry.py) | **NEW** | Optional developer utility script to parse, filter, and summarize NDJSON telemetry events from stdin or log files. | None | None |
| [`tests/test_observability.py`](file:///d:/Project_website/tests/test_observability.py) | **NEW** | Complete automated test suite covering log schemas, correlation propagation, PII redaction, telemetry taxonomy, and slow query detection. | None | CI execution |
| [`docs/00-project/PHASE-6.2.3-IMPLEMENTATION-REPORT.md`](file:///d:/Project_website/docs/00-project/PHASE-6.2.3-IMPLEMENTATION-REPORT.md) | **NEW** | Comprehensive implementation and verification report upon completion. | None | Documentation |

---

## 20. Scope, Non-Scope & Deferred Items

### In Scope for Phase 6.2.3
- Dual-mode structured logging (ANSI text for dev, NDJSON for prod).
- Request correlation ID propagation across responses and error envelopes.
- Request completion duration timing and slow request alerting.
- Native SQLAlchemy slow query probe (>500ms).
- In-house anonymous product telemetry emitter (`emit_telemetry_event`).
- 7 canonical discovery funnel events.
- Security event logging (rate limits, 403s, invalid session tokens) with IP hashing.
- AI Gateway fallback and latency telemetry.
- Contact form PII leak remediation in `app/routers/web.py`.
- Automated test coverage in `tests/test_observability.py`.

### Strictly Out of Scope
- Third-party analytics scripts (Google Analytics, PostHog, Plausible).
- Database-backed analytics tables or SQL Server telemetry storage.
- External monitoring daemons (Prometheus, Grafana, ELK, Datadog).
- Modification of database schema or Alembic migrations.
- Modification of Phase 5.3 FSM logic or domain state transitions.
- Modification of public frontend styling or visual designs.

### Deferred (Phase 6.2.4 & Beyond)
- Static asset immutable caching headers (`Cache-Control: public, max-age=31536000, immutable`).
- Advanced production reverse proxy configuration (Caddy / Nginx rate limit offloading).
- Formal production deployment playbooks and environment runbooks.

---

## 21. Owner Decisions Required

The following decisions require explicit owner direction and remain preserved as UNRESOLVED pending owner review:

1. **Slow Query Threshold Approval (UNRESOLVED):**
   - *Proposal:* Set slow SQL query logging threshold to **500 ms** (`slow_query_threshold_ms = 500.0`).
   - *Status:* Preserved as an unresolved owner decision for Phase 6.2.3 implementation.
2. **Dashboard Strategy Confirmation (UNRESOLVED):**
   - *Proposal:* Structured stdout telemetry + optional local inspection CLI (`scripts/inspect_telemetry.py`). Reject database-backed admin dashboards (Option C) and third-party SaaS (Option D).
   - *Status:* Preserved as an unresolved owner decision for Phase 6.2.3 implementation.
3. **Production Log Retention Baseline (UNRESOLVED):**
   - *Proposal:* Production log retention remains provider-dependent. No fixed production retention period is approved at MVP planning stage unless explicitly supported by authoritative documentation.
   - *Status:* Preserved as an unresolved owner decision for future production deployment planning.

---

## 22. Risks & Open Questions

| Risk / Question ID | Risk Description | Severity | Mitigation Strategy |
| :--- | :--- | :---: | :--- |
| **RSK-623-01** | Accidental PII leakage in telemetry payloads | High | Enforce strict schema validation in `emit_telemetry_event`; automatically filter out blacklisted keys (`name`, `email`, `phone`, `prompt`, `raw_text`). |
| **RSK-623-02** | Log stream saturation from automated health probes | Medium | Suppress `/health/live` and `/health/ready` requests from emitting INFO access logs; route to DEBUG only. |
| **RSK-623-03** | Performance degradation from SQL query timing | Low | Use lightweight native SQLAlchemy Core event hooks (`time.perf_counter()`); zero database round-trips. |
| **RSK-623-04** | Log volume growth on high traffic | Low | Emit structured events only on key state transitions and request completions; zero function-level tracing. |

---

## 23. Implementation Sequence (Upon Owner Approval)

```
Step 1: Configuration & Logging Primitives
  ├── Add log_format & threshold settings to app/config.py
  ├── Enhance JSONLogFormatter in app/shared/logging.py
  └── Author in-house telemetry emitter in app/shared/telemetry.py
        │
Step 2: Security & Remediation
  ├── Remediate PII email logging in app/routers/web.py:283
  └── Anonymize IP logging (hash_ip) in rate_limit_middleware
        │
Step 3: Middleware & Database Instrumentation
  ├── Update correlation_id_middleware for request access telemetry
  ├── Implement noise filtering for /health/* and /static/*
  └── Attach slow-query event listeners in app/database/connection.py
        │
Step 4: Domain & Gateway Telemetry Integration
  ├── Wire discovery funnel events into app/modules/discovery/service.py
  └── Wire fallback/latency telemetry into app/ai_gateway/gateway.py
        │
Step 5: Automated Verification & Documentation
  ├── Author tests/test_observability.py
  ├── Verify all tests pass locally and in GitHub Actions CI (92 baseline + new tests)
  ├── Verify Ruff, Bandit, and pip-audit pass cleanly
  └── Produce docs/00-project/PHASE-6.2.3-IMPLEMENTATION-REPORT.md
```

---

## 24. Governance Checklist

- [x] **Phase 5.3 remains immutable:** Discovery state machine, schemas, and services preserved without architectural mutation.
- [x] **Phase 5.4/5.5 public website remains intact:** All public pages, pillars, and Jinja2 templates preserved.
- [x] **Phase 6.1 security hardening remains intact:** Security headers, rate limiting, and cookie security preserved.
- [x] **Phase 6.2.1 CI/CD remains intact:** GitHub Actions workflow with SQL Server 2022 container preserved.
- [x] **Phase 6.2.2 static-analysis gates remain intact:** Ruff, Bandit, and pip-audit quality gates maintained.
- [x] **SQL Server remains the only database architecture:** Zero PostgreSQL, SQLite, MongoDB, or vector databases.
- [x] **No Redis:** Rate limiting and session handling remain process-local.
- [x] **No PostgreSQL:** Preserved SQL Server dialect exclusively.
- [x] **No SQLite:** Preserved real SQL Server container in CI.
- [x] **No new microservices:** Preserved modular monolith architecture.
- [x] **No frontend framework migration:** Preserved Jinja2 + HTMX + Alpine.js.
- [x] **AI Gateway remains provider-neutral:** Zero vendor lock-in or proprietary SDKs.
- [x] **No third-party analytics scripts:** Zero Google Analytics, Meta Pixel, PostHog, or Plausible scripts.
- [x] **No unnecessary runtime dependencies:** Zero packages added to `requirements.txt`.
- [x] **No database schema changes:** Zero new tables or migrations proposed.
- [x] **No unsupported privacy/compliance claims:** Avoided speculative legal or SOC 2 claims.
- [x] **No raw PII in telemetry:** Strict pre-emission sanitization and key dropping.
- [x] **No secrets in logs:** Global regex filtering and sensitive parameter masking.
- [x] **Existing correlation ID preserved:** Outbound headers and ContextVar propagation intact.
- [x] **Existing rate limiter preserved:** In-memory sliding window retained.
- [x] **Existing PII scrubber preserved:** `scrub_pii()` integrated into logging and telemetry.
- [x] **₹0 MVP infrastructure principle preserved:** Zero new operational costs.

---

## 25. Final Planning Status

### PHASE 6.2.3 PLANNING COMPLETE — AWAITING OWNER APPROVAL

**HARD STOP:** Phase 6.2.3 implementation has NOT been started. No application code, configuration files, test suites, or database migrations have been modified. Awaiting formal owner approval of this planning report and associated decision items before proceeding to execution.
