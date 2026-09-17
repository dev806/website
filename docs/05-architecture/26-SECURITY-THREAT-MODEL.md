# Application Security Threat Model (STRIDE Methodology)

**Document ID:** `DOC-ARCH-026`  
**Classification:** Security Architecture / Phase 4 Threat Modeling  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Security Architecture](file:///d:/Project_website/docs/05-architecture/14-SECURITY-ARCHITECTURE.md) | [AI Safety & Governance](file:///d:/Project_website/docs/05-architecture/12-AI-SAFETY-AND-GOVERNANCE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Threat Modeling Methodology

The threat model of `[STUDIO_NAME]` applies the industry-standard **STRIDE** methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) to evaluate every boundary interface, data store, and external dependency across the web platform.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              STRIDE THREAT CATEGORIES                                  │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ THREAT CATEGORY       │ PRIMARY ATTACK TARGET      │ SYSTEM DEFENSE POSTURE            │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ S - Spoofing          │ Session cookies, identity. │ Cryptographic HMAC signing.       │
│ T - Tampering         │ Form payloads, CSRF tokens.│ CSRF defense + Pydantic typing.   │
│ R - Repudiation       │ Consent, architect review. │ Immutable timestamped audit logs. │
│ I - Info Disclosure   │ Confidential problem text. │ Provider evaluation + PII scrubs. │
│ D - Denial of Service │ LLM API costs, SQL pools.  │ SlowAPI IP limits + task bounds.  │
│ E - Privilege Elev.   │ Unlocked blueprint access. │ Strict session ownership checks.  │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 2. Comprehensive STRIDE Threat Evaluation Matrix

---

### S: Spoofing Identity
* **Threat S1: Session Cookie Forgery**: Attacker crafts an arbitrary session cookie to hijack an existing client's diagnostic brief.
  - *Impact*: High. Unauthorized access to confidential problem text and blueprint.
  - *Likelihood*: Low.
  - *Mitigation*: Cookies are signed with `itsdangerous` using a 64-character server `SECRET_KEY`. Tampered cookies fail cryptographic signature checks and are discarded.
  - *Residual Risk*: Low. Bounded by secret key confidentiality.

* **Threat S2: Magic Link Token Replay**: Attacker intercepts and replays a recovery link across devices.
  - *Impact*: Medium. Access to archived diagnostic brief.
  - *Likelihood*: Low.
  - *Mitigation*: Magic link tokens use short 7-day expiration windows and SHA-256 hash checking.

---

### T: Tampering With Data
* **Threat T1: Client-Side Pricing Manipulation**: Attacker attempts to tamper with hidden form fields to force an indicative budget to display ₹0.
  - *Impact*: Critical commercial liability.
  - *Likelihood*: Medium.
  - *Mitigation*: **Zero client-side trust**. All budget and timeline calculations occur 100% server-side in Python (`EstimationService`). The client cannot manipulate sizing parameters.
  - *Residual Risk*: Negligible.

* **Threat T2: SQL Injection via Problem Input**: Attacker injects T-SQL commands (`'; DROP TABLE leads;--`) into the problem textarea.
  - *Impact*: Catastrophic data loss.
  - *Likelihood*: High attempt frequency.
  - *Mitigation*: All queries run via SQLAlchemy 2.x parameterized expressions. Input is strictly treated as text literals.
  - *Residual Risk*: Very low for ORM queries; residual risk remains in raw SQL escape scenarios (which are strictly barred by engineering conventions).

---

### R: Repudiation
* **Threat R1: Denial of Legal Consent**: Lead claims they never authorized their email to receive blueprint materials.
  - *Impact*: Privacy compliance friction (`BD-014`).
  - *Likelihood*: Low.
  - *Mitigation*: `dbo.lead_consents` logs exact UTC timestamp, consent version text, and hashed IP address.

---

### I: Information Disclosure
* **Threat I1: Prompt Injection Data Exfiltration**: Attacker submits adversarial prompts designed to force the LLM to output environment variables, database passwords, or internal system instructions.
  - *Impact*: High.
  - *Likelihood*: High attempt frequency.
  - *Mitigation*: Hardened XML prompt tags (`DOC-ARCH-012`), strict Pydantic output parsing (discards free-form chat outputs), and strict isolation of secrets outside LLM context windows.
  - *Residual Risk*: Low.

* **Threat I2: Public Model Training on Client Data**: External AI vendor utilizes confidential operational problem descriptions for foundation model training.
  - *Impact*: Severe breach of client confidentiality.
  - *Likelihood*: Critical if using consumer APIs without contractual safeguards.
  - *Mitigation*: Mandatory evaluation of selected commercial AI providers to ensure enforceable non-training and data-use terms (`BD-014`), combined with automated regex PII scrubbing prior to outbound transmission. Provider contractual terms verification remains: `RESEARCH / TECHNICAL VALIDATION REQUIRED`.

---

### D: Denial of Service (DoS)
* **Threat D1: Automated AI API Cost Exhaustion**: Bot script floods `/api/v1/discovery/problem` with rapid requests to trigger massive third-party LLM token fees.
  - *Impact*: Financial cost explosion.
  - *Likelihood*: High.
  - *Mitigation*: Strict IP-based rate limiting (SlowAPI: max 5 requests/min per IP); Cloudflare bot management in production; circuit breaker limits daily token budget.

* **Threat D2: Database Connection Pool Starvation**: Flooding slow queries to consume all SQL Server connection pool slots.
  - *Impact*: Application unresponsiveness (503 Service Unavailable).
  - *Likelihood*: Medium.
  - *Mitigation*: SQLAlchemy `QueuePool` timeout (30s) + Read Committed Snapshot Isolation (RCSI) preventing query deadlocks.

---

### E: Elevation of Privilege
* **Threat E1: Unlocked Blueprint Access Bypassing Lead Gate**: User manipulates client DOM or API calls to view Stage 5 Blueprint sections without providing corporate email.
  - *Impact*: Loss of top-of-funnel conversion qualification (`BD-005`).
  - *Likelihood*: High attempt frequency.
  - *Mitigation*: The server evaluates `session.is_unlocked == True` in SQL Server before rendering blueprint HTML partials or returning JSON. Client-side state is completely unauthoritative.
  - *Residual Risk*: Zero.
