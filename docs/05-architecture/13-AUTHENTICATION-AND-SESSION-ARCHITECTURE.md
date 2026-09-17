# Authentication & Session Architecture Specification

**Document ID:** `DOC-ARCH-013`  
**Classification:** Security & Identity / Phase 4 Session Architecture  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [ADR-010](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md#adr-010)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Identity Principles: Frictionless & Progressive

In strict compliance with Owner Decision `BD-005`, `[STUDIO_NAME]` **rejects mandatory upfront user registration**. Forcing users to create a password or perform OAuth social logins before experiencing value creates severe drop-off.

The identity architecture operates as a **progressive three-tier elevation model**:
1. **Tier 1: Anonymous Ephemeral Session**: Bound by a signed HTTP-only cookie; allows full Stage 1–4 discovery exploration.
2. **Tier 2: Elevated Lead Session**: Activated upon progressive lead capture (Name + Email); unlocks full 18-section Solution Blueprint and indicative estimates.
3. **Tier 3: Magic Link Recovery Session**: Allows clients to securely resume their diagnostic session from another device or after cookie clearance.

---

## 2. Session Token Cryptographic Specification

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SESSION TOKEN ANATOMY & LIFECYCLE                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   COOKIE NAME: `studio_session_id`                                                     │
│   PAYLOAD STRUCTURE: `<UUID4_SESSION_ID>.<TIMESTAMP>.<HMAC_SHA256_SIGNATURE>`         │
│                                                                                        │
│   FLAGS:                                                                               │
│   • `HttpOnly = True`       (Inaccessible to client-side JavaScript / XSS proof)       │
│   • `SameSite = Lax`        (Protects against Cross-Site Request Forgery / CSRF)       │
│   • `Secure = False`        (Localhost development at ₹0 cost)                         │
│   • `Secure = True`         (Enforced in production over HTTPS)                        │
│   • `Max-Age = 2,592,000`   (Candidate lifetime: Policy Decision Required)             │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### A. Signing & Verification Implementation
- The cookie payload is signed using Python's `itsdangerous.TimestampSigner` initialized with `SECRET_KEY` from application settings.
- The server validates the cryptographic signature on every request. Tampered cookies are immediately rejected and replaced with a fresh anonymous session.
- **Database Hash Isolation**: The server never stores the raw cookie token in the database. It stores the SHA-256 hash (`session_token_hash`), protecting session identity against database leakages.

---

## 3. Magic Link Session Recovery Protocol

When a lead unlocks their Solution Blueprint, they receive an automated email containing a **secure one-time recovery URL**:
```text
https://studio.com/discovery/review?token=eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

### Recovery Flow
1. **Token Generation**: Generates a signed, time-limited JSON Web Signature (JWS) containing `{ "session_id": "...", "exp": 1725720000 }` valid for **7 days**.
2. **Token Redemption**: When clicked, the FastAPI route validates the token signature, sets a fresh `studio_session_id` cookie on the client's browser, and redirects to the unlocked Blueprint view.
3. **Replay Protection**: Redeemed magic links are recorded in memory/database to prevent token reuse after formal review initiation.

---

## 4. CSRF Defense Architecture for HTMX

Because HTMX dispatches AJAX requests for discovery state updates, the application enforces a robust **double-submit cookie or header-based CSRF defense**:
1. On initial GET request, FastAPI generates a cryptographic CSRF token stored in a `studio_csrf` cookie.
2. The Jinja2 layout injects this token into the global HTMX configuration:
   ```html
   <body hx-headers='{"X-CSRF-Token": "{{ csrf_token }}"}'>
   ```
3. A FastAPI dependency validates `X-CSRF-Token` on all incoming `POST`/`PUT`/`DELETE` requests. Requests failing validation return `403 Forbidden`.
