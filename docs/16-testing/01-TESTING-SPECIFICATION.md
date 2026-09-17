# PHASE 6 — TESTING & QA SPECIFICATION

**Document ID:** `DOC-TEST-001`  
**Classification:** Testing Architecture & QA Specification  
**Parent Horizon:** Phase 6 (Rigor, Security & Reliability)  
**Status:** CANONICAL SPECIFICATION — RECONCILED & CORRECTED — AWAITING OWNER APPROVAL  

---

## 1. QA PHILOSOPHY: EMPIRICAL VERIFICATION

The QA strategy of `[STUDIO_NAME]` is engineered around a core law: **no task is complete until automated tests empirically prove correct behavior without breaking existing functionality**.

We prioritize **high-value integration, state machine, security, API contract, and regression testing**.

---

## 2. PRECISE TEST SUITE METRICS & TERMINOLOGY

- **Test Cases Passed**: **85 total passing test cases** (0 failures, 0 errors, 0 skipped).
  - Main application test suite: **78 passing test cases** (`pytest tests/ -v`).
  - Sprint 0 baseline regression suite: **7 passing test cases** (`pytest spikes/test_sprint0_suite.py -v`).
- **Assertions Evaluated**: ~240 individual Python `assert` statements evaluated across the 85 test cases.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CURRENT TEST SUITE MATRIX                                 │
├───────────────────────────────────┬───────────────────┬────────────────────────────────┤
│ TEST SUITE FILE                   │ TEST COUNT        │ PRIMARY PURPOSE                │
├───────────────────────────────────┼───────────────────┼────────────────────────────────┤
│ tests/test_public_website.py      │ 17 GET + 4 Func   │ 17 GET routes, SEO, SVG icons  │
│ tests/test_discovery_api.py       │ 4 Tests           │ API contracts & Stepper flows  │
│ tests/test_discovery_ux.py        │ 8 Tests           │ Full 7-stage journey & FSM     │
│ tests/test_discovery_service.py   │ 7 Tests           │ Service logic & PII scrubbing  │
│ tests/test_fsm.py                 │ 9 Tests           │ State machine guard & unlock   │
│ tests/test_ai_gateway.py          │ 5 Tests           │ PII scrub, timeout & fallback  │
│ tests/test_database.py            │ 3 Tests           │ SQL Server connection & commit │
│ tests/test_models.py              │ 3 Tests           │ ORM models & relationships     │
│ tests/test_estimation.py          │ 2 Tests           │ Server-side estimation logic   │
│ tests/test_config.py              │ 4 Tests           │ Settings & secret masking      │
│ tests/test_health.py              │ 3 Tests           │ Live & readiness probes        │
│ tests/test_exceptions.py          │ 1 Test            │ 404 JSON error envelopes       │
│ tests/test_frontend.py            │ 2 Tests           │ Base layout & static assets    │
│ tests/test_alembic_lifecycle.py   │ 1 Test            │ Migration upgrade/downgrade    │
├───────────────────────────────────┼───────────────────┼────────────────────────────────┤
│ spikes/test_sprint0_suite.py      │ 7 Tests           │ Sprint 0 baseline regression   │
├───────────────────────────────────┼───────────────────┼────────────────────────────────┤
│ TOTAL AUTOMATED TEST CASES        │ 85 PASSED (100%)  │ ZERO FAILING TEST CASES        │
└───────────────────────────────────┴───────────────────┴────────────────────────────────┘
```

---

## 3. SECURITY CONTROL TO TEST MAPPING MATRIX

| Security Control | Implementation Vector | Existing Test | Missing Test / Phase 6 Expansion |
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

## 4. EVALUATION OF HEAVY TESTING TOOLCHAINS

- **Playwright (Browser E2E)**: Evaluated adding Playwright Node/Python E2E testing framework. **Recommendation: DEFERRED / OPTIONAL**. The current FastAPI `TestClient` + HTML parsing tests validate DOM structure, links, and accessibility at **₹0 infrastructure cost** and **sub-second execution speed**.
- **k6 (Load Testing)**: Evaluated adding k6 scripts. **Recommendation: OPTIONAL LOCAL SCRIPT**. Performance checks can be executed via lightweight Python `httpx` async benchmarking scripts.
