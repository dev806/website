# Architecture Open Questions & Unresolved Decisions Register

**Document ID:** `DOC-ARCH-028`  
**Classification:** Systems Architecture / Phase 4 Open Decisions Ledger  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Architecture Decision Records](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Governance & Resolution Protocol

In accordance with project principles:
- **No proposal silently becomes an approval.**
- All open engineering decisions are maintained in this explicit ledger with transparent criteria, current working baselines, and downstream impact gates.

Classification taxonomy:
- **`Approved`**: Ratified owner decision.
- **`Recommended`**: Preferred architectural candidate awaiting formal sign-off.
- **`Technical Evaluation Required`**: Requires empirical code benchmarking during early implementation.
- **`Policy Decision Required`**: Strategic business or legal decision.
- **`Owner Decision Required`**: Direct business mandate.
- **`Decoupled / Future`**: Explicitly out of scope for the current development phase.

---

## 2. Register of Architecture Open Questions (`AOQ-001` through `AOQ-014`)

| ID | Decision Topic | Current Baseline / Hypothesis | Classification | Resolution Gate & Downstream Impact |
| :--- | :--- | :--- | :--- | :--- |
| **`AOQ-001`** | **Primary External AI Provider Selection** | Provider abstraction layer (`DOC-ARCH-010`). Candidate providers: Google, OpenAI, Anthropic. | `Technical Evaluation Required` | Evaluated via API latency, structured JSON reliability, and enterprise data-use/non-training terms. |
| **`AOQ-002`** | **Specific LLM Model Family for Discovery** | Candidate fast-tier models (e.g., `gemini-1.5-flash`, `claude-3-5-haiku`, `gpt-4o-mini`). | `Technical Evaluation Required` | Must support strict schema-constrained outputs with low latency and favorable per-token economics. |
| **`AOQ-003`** | **SQL Server Python Driver Concurrency Mode** | `pyodbc` synchronous driver executed within FastAPI threadpool (`run_in_threadpool` / `get_db`). `aioodbc` remains supported alternative. | `Confirmed Baseline (SP-03)` | *Historical Status:* `Technical Validation Required`. *Updated 2026-09-07:* SP-03 live benchmark on SQL Server 2022 Express confirmed `pyodbc` is ~2.8x faster (10.3ms vs 29.3ms avg) with 0 errors (`DOC-ARCH-SPRINT0-001`). |
| **`AOQ-004`** | **Production Compute & Cloud Hosting Provider** | Local development strictly confirmed as Uvicorn + MS SQL Server (₹0) (`BD-015`). Production compute open. | `Decoupled / Cost Evaluation Required` | Evaluated prior to public release (Linux VPS Docker Compose vs Managed Container PaaS vs Cloud). |
| **`AOQ-005`** | **Production Database Persistence Engine** | Local development strictly confirmed as Microsoft SQL Server + SSMS (`CST-CNF-008`). Production DB open. | `Decoupled / Architectural & Cost Evaluation Required` | Evaluated based on cloud licensing, managed database pricing, and dialect portability. |
| **`AOQ-006`** | **Transactional Email Service Provider** | Generic `IEmailService` interface. Local dev uses console mock logger (`DOC-ARCH-020`). Vendor unselected. | `Technical Evaluation Required` | Candidate providers evaluated based on deliverability, transactional pricing, and API reliability. |
| **`AOQ-007`** | **Anonymous Telemetry & Analytics Platform** | Zero-PII event stream specified (`DOC-ARCH-013`). Analytics vendor unselected. | `Technical Evaluation Required` | Self-hosted Umami vs Plausible vs Cloudflare Web Analytics evaluated based on zero-cookie compliance. |
| **`AOQ-008`** | **Diagnostic Data Retention Policy Schedule** | Purge sweeper capability built. Candidate baselines: 30 days anonymous, 7 days magic links, 90 days telemetry. | `Policy Decision Required` | Final retention durations must be ratified by Project Owner before production cleanup scheduler is activated. |
| **`AOQ-009`** | **Production Continuity & RPO / RTO Policy Targets** | Native SQL Server backup/restore capabilities specified. Numerical targets: candidate $< 4$h RPO / $< 2$h RTO. | `Proposed / Policy Decision Required` | Formal recovery time and point objectives require business and operational policy sign-off before production. |
| **`AOQ-010`** | **Static Asset Delivery & Vendoring Strategy** | Local vendoring of HTMX 2.0.4 and Alpine.js 3.14.8 inside `/static/vendor/` with zero CDN dependency. | `Confirmed Baseline (SP-07)` | *Historical Status:* `Recommended / Proposed`. *Updated 2026-09-07:* SP-07 verified local offline serving via FastAPI `StaticFiles` with HTTP 200 and correct MIME types (`DOC-ARCH-SPRINT0-001`). |
| **`AOQ-011`** | **Magic Link Token Expiration & Session Lifetime** | Signed cookie session manager (`DOC-ARCH-013`). Recommended: 7-day token expiration, 30-day session max. | `Policy Decision Required / Recommended` | Balances prospective client convenience against token exposure duration. |
| **`AOQ-012`** | **Automated DB Backup Storage Destination** | Native T-SQL backup scripts (`DOC-ARCH-023`). Destination: Local backup directory vs encrypted off-site cloud. | `Policy Decision Required / Technical Evaluation Required` | Local disk backup for dev; off-site storage target (e.g. S3-compatible / Backblaze B2) to be selected for prod. |
| **`AOQ-013`** | **Official Brand Name & Domain DNS Setup** | Parameterized as `[STUDIO_NAME]` (`BD-001`). Domain acquisition and DNS uncompleted. | `Owner Decision Required` | Required before production TLS certificates, domain-verified transactional email, and branding can be finalized. |
| **`AOQ-014`** | **SQL Server Architecture & Driver Compatibility Validation** | SQLAlchemy 2.0 MSSQL dialect + Alembic migrations + live SQL Server 2022 Express persistence. | `Confirmed Verified (SP-02, SP-04)` | *Historical Status:* `Technical Validation Required`. *Updated 2026-09-07:* Verified live on SQL Server 2022 Express. Models, DDL, RCSI, and rollback fully functional (`DOC-ARCH-SPRINT0-001`). |
