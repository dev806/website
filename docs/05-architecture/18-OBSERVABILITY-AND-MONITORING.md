# Observability, Structured Logging & Health Architecture

**Document ID:** `DOC-ARCH-018`  
**Classification:** DevOps & Reliability / Phase 4 Observability  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [ADR-015](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md#adr-015)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Observability Principles: Vendor-Agnostic & Structured

The observability architecture of `[STUDIO_NAME]` provides **complete operational visibility into application health, AI token consumption, and database performance at ₹0 licensing cost**.

In accordance with project governance:
- **Zero Paid APM Dependencies**: Rejects proprietary monitoring suites (Datadog, Dynatrace, New Relic) for local development and MVP.
- **Vendor-Agnostic Analytics Posture**: Selection of an analytics platform (e.g., self-hosted Umami, Plausible, Cloudflare Web Analytics) remains: `TECHNICAL EVALUATION REQUIRED`. Telemetry is dispatched via standard anonymous beacon endpoints (`/api/v1/telemetry`), ensuring provider changes never impact client code.
- **Machine-Readable JSON Standard**: All application events are emitted as structured JSON lines to standard output (`stdout`), easily ingested by Docker, Linux systemd journals, or open-source log forwarders.
- **Privacy Enforcement**: PII (emails, names) and proprietary problem descriptions are **strictly redacted** from log payloads.

---

## 2. Structured JSON Log Schema (`structlog`)

Every log entry conforms to a standardized JSON schema (illustrative schema):
```json
{
  "timestamp": "2026-09-07T14:45:12.102Z",
  "level": "info",
  "event": "discovery_stage_completed",
  "request_id": "9f1a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "module": "discovery",
  "stage": "OPPORTUNITY_MAP_GENERATED",
  "duration_ms": 142.5,
  "ai_telemetry": {
    "model": "candidate-model-id",
    "prompt_tokens": 480,
    "completion_tokens": 310,
    "total_tokens": 790,
    "estimated_cost_usd": 0.0001
  }
}
```

---

## 3. Dedicated Health Check Endpoints

FastAPI exposes two standard health probes for container orchestration and uptime monitoring:

### A. Liveness Probe (`GET /health/live`)
* **Purpose**: Verifies that the Uvicorn ASGI process is alive and accepting connections.
* **Checks**: Process responsiveness.
* **Response**: `{"status": "alive", "uptime_seconds": 3600}` (`HTTP 200 OK`).

### B. Readiness Probe (`GET /health/ready`)
* **Purpose**: Verifies that the application is ready to serve client traffic, including active database connectivity.
* **Checks**: Executes a lightweight test query against Microsoft SQL Server (`SELECT 1`).
* **Response (`200 OK`)**:
  ```json
  {
    "status": "ready",
    "database": {
      "engine": "Microsoft SQL Server",
      "status": "connected",
      "latency_ms": 2.4
    }
  }
  ```
* **Failure Response (`503 Service Unavailable`)**: Emitted if SQL Server connection fails.

---

## 4. Security & Audit Telemetry

The following security events trigger high-priority warning/error logs:
1. **`CSRF_TOKEN_INVALID`**: Mismatched or missing CSRF token on mutating POST.
2. **`RATE_LIMIT_EXCEEDED`**: Client IP exceeded discovery submission threshold.
3. **`PII_SCRUBBED`**: Sensitive credit card or credential pattern detected and stripped from input text.
4. **`SUSPECTED_PROMPT_INJECTION`**: Input text containing explicit jailbreak or instruction override tokens.
