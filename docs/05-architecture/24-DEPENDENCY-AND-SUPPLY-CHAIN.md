# Dependency Management & Software Supply Chain Specification

**Document ID:** `DOC-ARCH-024`  
**Classification:** DevOps & Security / Phase 4 Supply Chain Security  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Security Architecture](file:///d:/Project_website/docs/05-architecture/14-SECURITY-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Supply Chain Philosophy: Radical Dependency Minimization

The software supply chain of `[STUDIO_NAME]` enforces a strict principle: **every external package is an operational liability, maintenance tax, and attack surface**.

We ruthlessly minimize third-party libraries:
- **Zero Node.js / npm Ecosystem**: The frontend uses vendor-downloaded, single-file scripts (`htmx.min.js`, `alpine.min.js`), completely eliminating npm supply-chain vulnerabilities.
- **Strictly Pinned Dependencies**: All Python packages are pinned to exact semantic versions in `requirements.txt` with SHA-256 hash checking.
- **Permissive Open-Source Licensing**: Every third-party library must possess a permissive open-source license (MIT, Apache 2.0, BSD-3-Clause). Viral copyleft licenses (GPL, AGPL) are strictly barred.

---

## 2. Core Dependencies & Asset Baseline (Recommended Candidates)

The packages below represent the **recommended candidate baseline**, subject to empirical verification during Phase 5 Sprint 0 setup:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   RECOMMENDED PYTHON RUNTIME LIBRARIES (CANDIDATE BASELINE)            │
├───────────────────────┬────────────────────┬───────────┬───────────────────────────────┤
│ PACKAGE NAME          │ TARGET / CANDIDATE │ LICENSE   │ STATUS / ARCHITECTURAL ROLE   │
├───────────────────────┼────────────────────┼───────────┼───────────────────────────────┤
│ `fastapi`             │ `== 0.115.*`       │ MIT       │ APPROVED (BD-015) ASGI Core   │
│ `uvicorn[standard]`   │ `== 0.30.*`        │ BSD       │ RECOMMENDED ASGI Server       │
│ `pydantic`            │ `== 2.9.*`         │ MIT       │ APPROVED (BD-015) Validation  │
│ `pydantic-settings`   │ `== 2.5.*`         │ MIT       │ RECOMMENDED Config            │
│ `sqlalchemy`          │ `== 2.0.*`         │ MIT       │ APPROVED (BD-015) ORM/Core    │
│ `alembic`             │ `== 1.13.*`        │ MIT       │ APPROVED (BD-015) Migrations  │
│ `pyodbc`              │ `== 5.1.*`         │ MIT       │ APPROVED (CST-CNF-008) Sync DB│
│ `aioodbc`             │ `== 0.5.*`         │ Apache-2.0│ TECHNICAL VALIDATION REQUIRED │
│ `jinja2`              │ `== 3.1.*`         │ BSD       │ APPROVED (BD-015) SSR HTML    │
│ `python-multipart`    │ `== 0.0.*`         │ Apache-2.0│ RECOMMENDED Form Parsing      │
│ `itsdangerous`        │ `== 2.2.*`         │ BSD       │ RECOMMENDED Session Signing   │
│ `structlog`           │ `== 24.4.*`        │ Apache-2.0│ RECOMMENDED Structured Logs   │
│ `httpx`               │ `== 0.27.*`        │ BSD       │ RECOMMENDED HTTP Client       │
├───────────────────────┼────────────────────┼───────────┼───────────────────────────────┤
│ FRONTEND ASSET CANDIDATES (RECOMMENDED: LOCAL VENDORING / CANDIDATE: CDN + SRI)        │
├───────────────────────┼────────────────────┼───────────┼───────────────────────────────┤
│ `htmx.min.js`         │ `2.0.* (~14KB)`    │ BSD-2     │ RECOMMENDED (BD-015) DOM Swap │
│ `alpine.min.js`       │ `3.14.* (~15KB)`   │ MIT       │ RECOMMENDED (BD-015) UI State │
└───────────────────────┴────────────────────┴───────────┴───────────────────────────────┘
```

> **STATIC ASSET STRATEGY NOTE:** Vendoring HTMX and Alpine.js locally inside `/static/vendor/` is **RECOMMENDED** to avoid third-party CDN points-of-failure. Loading via public CDN with Subresource Integrity (SRI) hashes remains an evaluated alternative (`AOQ-013`). Zero Node.js or npm build tooling is introduced.

---

## 3. Vulnerability Scanning & Audit Protocol

1. **Automated Vulnerability Auditing**: The continuous integration pipeline runs `pip-audit` on every commit, asserting zero known Common Vulnerabilities and Exposures (CVEs) in pinned packages:
   ```bash
   pip-audit -r requirements.txt --strict
   ```
2. **Secret Leak Prevention**: Pre-commit hooks run `detect-secrets` and `gitleaks` to block accidental commits of `.env` files, private keys, or API tokens.
3. **Third-Party AI SDK Risk Mitigation**: If an external LLM SDK releases a breaking update or deprecated dependency, the AI Gateway's abstract interface (`DOC-ARCH-010`) prevents cascading breakage to application domain code.
