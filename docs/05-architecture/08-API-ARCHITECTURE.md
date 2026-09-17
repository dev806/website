# API Architecture & Internal Interface Conventions

**Document ID:** `DOC-ARCH-008`  
**Classification:** System Architecture / Phase 4 API Engineering  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [API Contracts](file:///d:/Project_website/docs/05-architecture/09-API-CONTRACTS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Dual Interface Strategy: HTMX Partials & Structured JSON

The web application exposes a **clean, dual-response API surface**:
1. **Server-Driven UI Endpoints (HTMX Partials)**: Returns rendered HTML fragments for direct DOM morphing during interactive diagnostic navigation.
2. **Structured REST Endpoints (`/api/v1/*`)**: Returns strongly-typed JSON payloads validated by Pydantic v2 for telemetry, programmatic data access, and future mobile/portal clients.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI DUAL RESPONSE PIPELINE                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   INCOMING REQUEST ──➔ [FastAPI Ingress Router]                                        │
│                               │                                                        │
│               ┌───────────────┴───────────────┐                                        │
│               ▼                               ▼                                        │
│      [Accept: text/html]             [Accept: application/json]                        │
│               │                               │                                        │
│               ▼                               ▼                                        │
│   Jinja2 Partial Template            Pydantic v2 Serializer                            │
│   (HTML fragment swapped by HTMX)    (Standard JSON Envelope: `data` / `error`)        │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Universal REST Conventions & URL Taxonomy

All routes adhere to strict, predictable naming conventions:
* **Resource-Centric Naming**: Plural nouns (e.g. `/api/v1/discovery-sessions`, `/api/v1/leads`).
* **Sub-Resource Nesting**: Logical parent-child relationships (e.g. `/api/v1/discovery-sessions/{id}/opportunities`).
* **Kebab-Case Slugs**: Lowercase hyphenated paths for legibility.
* **HTTP Method Semantics**:
  - `GET`: Idempotent resource retrieval. Zero side effects.
  - `POST`: Creation of new entities or triggering state machine transitions.
  - `PUT / PATCH`: Full or partial resource updates.
  - `DELETE`: Soft deletion of resources.

---

## 3. Standard Response Envelopes & Error Handling

### A. Successful JSON Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "8f9a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
    "timestamp": "2026-09-07T14:32:10.451Z"
  }
}
```

### B. Standard Error Envelope
All application errors (4xx and 5xx) return a uniform error structure preventing stack trace leakage:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The problem description must contain at least 20 characters.",
    "details": [
      {
        "field": "raw_text",
        "issue": "String should have at least 20 characters"
      }
    ]
  },
  "meta": {
    "request_id": "8f9a2b3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
    "timestamp": "2026-09-07T14:32:10.451Z"
  }
}
```

---

## 4. HTTP Status Code Hierarchy

| Status Code | Semantic Meaning | Application Usage in `[STUDIO_NAME]` |
| :--- | :--- | :--- |
| **`200 OK`** | Request succeeded. | Standard retrieval and successful HTMX HTML partial swaps. |
| **`201 Created`** | New entity created. | Successful creation of a `DiscoverySession` or `Lead`. |
| **`400 Bad Request`** | Malformed input. | Missing headers or unparseable form bodies. |
| **`401 Unauthorized`** | Missing authentication. | Invalid or expired magic link session recovery token. |
| **`403 Forbidden`** | Insufficient permission. | Attempting to access an unowned session's private lead data. |
| **`404 Not Found`** | Resource does not exist. | Invalid session UUID or missing blueprint ID. |
| **`422 Unprocessable`** | Pydantic validation failure. | Form validation errors (invalid email format, empty text). |
| **`429 Too Many Req`** | Rate limit throttled. | Exceeded discovery submission threshold (SlowAPI). |
| **`500 Internal Error`** | Server error. | Unhandled exceptions; returns safe generic message with request ID. |

---

## 5. Security Controls & Rate Limiting

1. **Request Correlation IDs (`X-Request-ID`)**: Every HTTP request receives an immutable UUID4 tracking identifier injected into logging and response headers.
2. **CSRF Protection**: For state-mutating requests (`POST`/`PUT`/`DELETE`), the application verifies a cryptographically signed CSRF token passed via header `X-CSRF-Token` or form field `csrf_token`.
3. **Adaptive Rate Limiting**:
   - `POST /api/v1/discovery-sessions/problem`: Max 5 submissions per minute per IP to prevent LLM API cost abuse.
   - `POST /api/v1/leads`: Max 10 submissions per hour per IP to prevent spam injection.
4. **Idempotency Keys**: Critical lead creation and review requests accept an optional `Idempotency-Key` header preventing duplicate record creation during client-side retries.
