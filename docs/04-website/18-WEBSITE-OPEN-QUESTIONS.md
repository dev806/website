# Website Open Questions & Unresolved Decisions Register

**Document ID:** `DOC-WEB-018`  
**Classification:** Website Architecture / Phase 3 Open Decisions Ledger  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-003](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-003), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Brand Open Questions](file:///d:/Project_website/docs/02-brand/08-BRAND-OPEN-QUESTIONS.md) | [Product Open Questions](file:///d:/Project_website/docs/03-product/12-PRODUCT-OPEN-QUESTIONS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Governance & Resolution Protocol

In accordance with project principles, unresolved website questions are maintained in this explicit ledger. **No assumption is converted into an approved decision without formal evaluation or owner sign-off.**

Each item is classified under strict resolution categories:
- **`Owner Decision Required`**: Strategic choice requiring direct owner sign-off.
- **`Research Required`**: External data or market analysis required.
- **`Validation Required`**: Empirically tested via user interactions or client feedback.
- **`Technical Evaluation (Phase 4)`**: Engineering benchmarking during technical specification.
- **`Deferred to Phase 2 / Future`**: Out of scope for MVP.

---

## 2. Unresolved Website Decisions Ledger (`WOQ-001` through `WOQ-010`)

| ID | Topic & Decision Context | Current Baseline / Hypothesis | Classification | Resolution Gate & Downstream Dependency |
| :--- | :--- | :--- | :--- | :--- |
| **`WOQ-001`** | **Official Brand Name & Domain Identity** | Working title is strictly parameterized as `[STUDIO_NAME]` (`BD-001`). Primary domain TLD is unfinalized. | `Owner Decision Required` | Prerequisite for production DNS setup, SSL certificates, and social card branding in Phase 4. |
| **`WOQ-002`** | **Visual Logo Mark & Brand Asset Design** | Placeholder typography lockup specified in design tokens. Final vector mark uncreated. | `Design Phase / Owner Decision` | Required prior to public frontend asset bundling. Zero impact on architecture. |
| **`WOQ-003`** | **Typography Licensing & Local Font Hosting** | Modern geometric sans-serif (e.g. Inter / Geist / Plus Jakarta Sans) + clean monospace font. | `Technical Evaluation (Phase 4)` | Self-hosted WOFF2 font files evaluated during Phase 4 to eliminate third-party Google Fonts tracking. |
| **`WOQ-004`** | **Exact Color Palette Hex Bindings** | Dark obsidian base with deep radial indigo/violet accents (`BD-012`). Exact hex codes uncommitted. | `Design Phase (Phase 4 CSS)` | Hex tokens to be bound in `index.css` variables during frontend engineering. |
| **`WOQ-005`** | **Analytics Vendor Selection (Zero-PII)** | Lightweight telemetry schema defined (`DOC-WEB-013`). Vendor (Plausible vs PostHog vs Cloudflare) undecided. | `Technical Evaluation (Phase 4)` | Selected during DevOps/Analytics phase based on self-hosting ease and zero-cookie posture. |
| **`WOQ-006`** | **Empirical Search Volumes & Keyword Difficulty** | Search intent clusters defined (`DOC-WEB-012`). Quantitative search volumes unmeasured. | `Research Required` | Empirical Google Search Console / Ahrefs data to be gathered post-launch. Zero fabricated data permitted. |
| **`WOQ-007`** | **Initial Client Case Study Availability** | Dedicated `/case-studies` deferred to Phase 2 (`PRD-MVP-002`) to prevent fabricated proof (`BR-GDL-003`). | `Validation Required (Phase 2)` | Activated once the first 2–3 client engagements yield verifiable production metrics. |
| **`WOQ-008`** | **Formal Legal Counsel Review for Terms & Privacy** | Best-practice compliance-ready privacy and terms drafted (`BD-014`). Statutory audit unperformed. | `Legal Action Required` | Legal review by external counsel recommended prior to processing high-liability enterprise data. |
| **`WOQ-009`** | **Diagnostic Data Retention Duration** | Proposed default: 30 days for unclaimed anonymous drafts; indefinite for leads requesting review. | `Policy Decision Required` | Final data retention schedule to be ratified before production database schema is locked in Phase 4. |
| **`WOQ-010`** | **Production Hosting Infrastructure & Reverse Proxy** | Local development strictly confirmed as Uvicorn + MS SQL Server (₹0 cost) (`BD-015`). Production compute open. | `Technical Evaluation (Phase 4)` | Evaluated in Phase 4 (Docker Compose on Linux VPS vs Managed PaaS) based on budget and scaling. |
