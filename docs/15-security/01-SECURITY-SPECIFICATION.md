# PHASE 6 — APPLICATION & AI SECURITY SPECIFICATION

**Document ID:** `DOC-SEC-001`  
**Classification:** Security Architecture & Implementation Specification  
**Parent Horizon:** Phase 6 (Rigor, Security & Reliability)  
**Status:** CANONICAL SPECIFICATION — RECONCILED & CORRECTED — AWAITING OWNER APPROVAL  

---

## 1. SECURITY PHILOSOPHY: DEFENSE-IN-DEPTH

The security posture of `[STUDIO_NAME]` is engineered to be **privacy-first, compliance-ready, and resilient against web and AI-specific threats**.

We strictly reject unverified marketing claims (such as claiming SOC 2, ISO 27001, or GDPR certification prior to formal third-party audit). All security controls are empirically specified with concrete mitigations and residual risk bounds.

---

## 2. DISCOVERY & PUBLIC ENDPOINT SECURITY CONTROL MATRIX

Reconciled against active router implementations in `app/routers/discovery_views.py` and `app/routers/web.py`:

| Endpoint Path | HTTP Method | Access Level | State Mutating | Rate Limit Req. | CSRF Req. | Input Validation | Abuse Risk | Idempotency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET /discovery` | GET | Public | No | Low (30/min) | No | Session cookie verification | Low | Idempotent |
| `POST /discovery/start` | POST | Public | Yes | Low (10/min) | Yes | Reset token validation | Low | Idempotent |
| `POST /discovery/problem` | POST | Public | Yes | **High (5/min)**| Yes | 20–2000 chars + PII Scrub | **High** (Token drain) | Non-idempotent |
| `POST /discovery/answers` | POST | Session | Yes | Medium (15/min)| Yes | Valid radio option selection | Medium | Non-idempotent |
| `GET /discovery/stage/opportunity-map` | GET | Session | No | Low (30/min) | No | Stage permission guard | Low | Idempotent |
| `GET /discovery/stage/{stage_name}` | GET | Session | No | Low (30/min) | No | Stage permission guard | Low | Idempotent |
| `POST /discovery/unlock` | POST | Session | Yes | **High (5/min)**| Yes | Name, Email regex, Consent=True | **High** (Lead capture) | Non-idempotent |
| `POST /discovery/review` | POST | Session (Unlocked)| Yes | **High (5/min)**| Yes | Architect triage scope model | Medium | Non-idempotent |
| `POST /discovery/backtrack` | POST | Session | Yes | Medium (15/min)| Yes | Target stage validation | Low | Idempotent |
| `POST /contact` | POST | Public | Yes | **High (5/min)**| Yes | Name, Email regex, Msg + PII Scrub | **High** (Form spam) | Non-idempotent |

---

## 3. RATE LIMITING ARCHITECTURE EVALUATION

Evaluating rate-limiting implementations without introducing external Redis infrastructure:

- **Approach A (Recommended for MVP)**: **Native FastAPI In-Memory Sliding Window Middleware**.
  - *Mechanism*: In-memory sliding window counter dictionary (`defaultdict(list)`) keyed by client IP and route path.
  - *Pros*: Zero external dependencies, ₹0 cost, sub-millisecond overhead, simple Pytest testability.
  - *Limitation*: Memory counter resets on process restart and is bounded to single-worker processes.
- **Approach B**: **Reverse-Proxy / Edge Rate Limiting** (Cloudflare / Azure Front Door / IIS / Nginx).
  - *Mechanism*: Offloads rate limiting to edge network prior to application entry.
  - *Pros*: Protects Uvicorn workers completely from volumetric bot attacks.
  - *Recommendation*: Use Approach A for local development and single-instance environments; offload to Approach B for multi-worker production deployments without adding Redis.

---

## 4. SECURITY HEADERS DESIGN (COMPATIBLE WITH HTMX & ALPINE.JS)

Designed specifically to avoid breaking current Jinja2, HTMX, Alpine.js, and inline SVG components:

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; form-action 'self';
```

*Note: `'unsafe-inline'` is currently required for Alpine.js dynamic event evaluation (`@click`, `@keydown.escape`) and HTMX swap handlers until an Alpine CSP build is adopted.*

---

## 5. COMPLIANCE-READY LANGUAGE POLICY

Public copy must strictly adhere to claim governance:
- **Prohibited Wording**: "GDPR Certified", "SOC 2 Certified", "100% Unhackable", "Zero Security Risk".
- **Approved Wording**: "Privacy-First Architecture", "Automated Pre-Transit PII Sanitization", "Provider-Neutral AI Gateway", "Compliance-Ready Data Minimization".
