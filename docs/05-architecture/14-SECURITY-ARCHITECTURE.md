# Comprehensive Application Security Architecture

**Document ID:** `DOC-ARCH-014`  
**Classification:** Security Engineering / Phase 4 Security Baseline  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Security Threat Model](file:///d:/Project_website/docs/05-architecture/26-SECURITY-THREAT-MODEL.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Security Engineering Philosophy: Defense-in-Depth

The security posture of `[STUDIO_NAME]` is engineered to be **compliance-ready, privacy-first, and resilient against modern web and AI-specific threats** (`BD-014`). 

The architecture strictly rejects unverified marketing claims (such as claiming SOC 2 or HIPAA certification prior to audit verification). It defines concrete **controls, mitigations, residual risks, and empirical validation requirements**, explicitly rejecting claims of absolute security or guaranteed invulnerability.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 6 DEFENSE-IN-DEPTH TIERS                              │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ TIER 1: PERIMETER / INGRESS   │ TIER 2: TRANSPORT & HEADERS   │ TIER 3: APPLICATION    │
│ Rate limiting, IP throttling, │ Strict TLS, HSTS, CSP,        │ Pydantic validation,   │
│ payload size caps (20KB max). │ anti-framing, anti-sniffing.  │ CSRF tokens, sessions. │
├───────────────────────────────┼───────────────────────────────┼────────────────────────┤
│ TIER 4: AI GATEWAY JAIL       │ TIER 5: PERSISTENCE BOUNDARY  │ TIER 6: SECRETS & OPS  │
│ PII scrubbing, provider       │ Parameterized queries in      │ Pydantic-settings,     │
│ data-use policy evaluation.   │ SQLAlchemy; least-privilege DB│ zero hard-coded keys.  │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

## 2. Core Threat Defenses

### A. Injection Attacks (SQL Injection & Command Injection)
* **SQL Injection**: Systematically mitigated via **SQLAlchemy 2.x ORM and parameterized Core expressions**. Raw string concatenation (`f"SELECT ... WHERE id = {user_input}"`) is strictly prohibited and flagged via automated static analysis (Bandit).
* **Command Injection**: The application executes zero operating system shell commands or external subprocesses from web requests.

### B. Cross-Site Scripting (XSS)
* **Jinja2 Auto-Escaping**: Context-aware HTML escaping is enabled globally for all Jinja2 template files (`.html`, `.jinja2`). All variables (`{{ user_text }}`) are converted to safe HTML entities (`&lt;`, `&gt;`, `&quot;`).
* **Safe HTML Policy**: The application completely prohibits `|safe` filter usage on untrusted client inputs.
* **Content Security Policy (CSP)**:
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; form-action 'self';
  ```

### C. Cross-Site Request Forgery (CSRF)
* All state-mutating requests (`POST`, `PUT`, `DELETE`) require a valid cryptographic `X-CSRF-Token` header.
* Cookies enforce `SameSite=Lax` (or `SameSite=Strict`), preventing automated cross-origin browser execution.

### D. Server-Side Request Forgery (SSRF)
* The server never accepts arbitrary external URLs from clients to fetch or scrape.
* The only external outbound HTTP connections made by the application are to **pre-configured, hardcoded AI API endpoints** over encrypted TLS.

---

## 3. Mandatory Security Headers Specification

Every response emitted by FastAPI includes the following HTTP security headers:
```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()
Strict-Transport-Security: max-age=31536000; includeSubDomains (Production only)
```

---

## 4. Secrets Management & Operational Security

1. **Zero Hard-Coded Credentials**: API keys, database connection strings, and session signing keys are loaded strictly through environment variables via `pydantic-settings` (`DOC-ARCH-021`).
2. **Repository Protection**: `.gitignore` strictly excludes `.env`, `.env.local`, and credential files. Automated pre-commit hooks (`detect-secrets`) scan commits to block accidental secret leaks.
3. **Least-Privilege Database Access**: The database user account configured for the web application possesses only `SELECT`, `INSERT`, `UPDATE`, and `DELETE` permissions on specific `dbo` application tables. It possesses zero `sysadmin`, `db_owner`, or server-level administrative privileges.
