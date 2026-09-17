# Unresolved Product Decisions & Strategic Open Questions

**Document ID:** `DOC-PRD-012`  
**Classification:** Product Definition / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Product Strategy](file:///d:/Project_website/docs/03-product/02-PRODUCT-STRATEGY.md) | [Product Requirements](file:///d:/Project_website/docs/03-product/11-PRODUCT-REQUIREMENTS.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Active Product Open Questions Register

---

## 1. Executive Summary & Governance Rules

In strict compliance with project governance and assumption management rules:
1. No unvalidated product hypothesis is treated as an established technical or commercial fact.
2. The foundational model **Free AI Diagnostic $\rightarrow$ Paid Discovery Sprint** (`BD-004`) is confirmed, but all detailed packaging, pricing, duration, and crediting parameters remain explicitly classified as `HYPOTHESIS — VALIDATION REQUIRED`.
3. Every open question is assigned a definitive classification, an architectural impact level, and an explicit resolution gate.

---

## 2. Master Product Open Questions Ledger

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        MASTER PRODUCT OPEN QUESTIONS TABLE                       │
├─────────┬───────────────────────────────┬────────────────────────┬───────────────┤
│ Item ID │ Topic Area                    │ Governance Status      │ Impact Layer  │
├─────────┼───────────────────────────────┼────────────────────────┼───────────────┤
│ POQ-001 │ Discovery Sprint Commercials  │ HYPOTHESIS — VALIDATION│ Pricing / SOW │
│ POQ-002 │ Exact AI Provider & Failover  │ TECHNICAL BENCHMARK    │ AI Engine API │
│ POQ-003 │ LLM Model Tiering Selection   │ RESEARCH REQUIRED      │ Cost / Latency│
│ POQ-004 │ Estimation Calibration Weights│ RESEARCH REQUIRED      │ Algorithmic DB│
│ POQ-005 │ Discovery Data Retention Limit│ OWNER DECISION REQ.    │ DB Purge Job  │
│ POQ-006 │ Product Telemetry Engine      │ TBD — PHASE 3 UX       │ Event Pipeline│
│ POQ-007 │ Session Resumption Mechanism  │ PROPOSED — PHASE 2     │ Auth / Cookies│
│ POQ-008 │ PDF Generation Technology     │ TBD — PHASE 2          │ Headless Tool │
│ POQ-009 │ Online Sprint Checkout Gate   │ REJECTED FOR MVP       │ E-Commerce    │
│ POQ-010 │ Dedicated Client Portal Need  │ DEFERRED — FUTURE      │ Full App Scope│
│ POQ-011 │ Production Hosting Decoupling │ TBD — PRE-DEPLOYMENT   │ Cloud Topology│
│ POQ-012 │ Multi-Language UI Support     │ OWNER DECISION REQ.    │ i18n Jinja2   │
└─────────┴───────────────────────────────┴────────────────────────┴───────────────┘
```

---

## 3. Detailed Item Analysis

---

### `POQ-001`: Paid Discovery Sprint Packaging, Pricing & Crediting Terms
* **Current State**: Approved strategic model is **Free AI Diagnostic $\rightarrow$ Paid Discovery Sprint** (`BD-004`).
* **Governance Status**: `HYPOTHESIS — VALIDATION REQUIRED`
* **Context**: While the two-tier concept is locked, specific commercial packaging details must be validated through market willingness-to-pay testing:
  - *Sprint Duration*: Is a 1-week (5 business day) sprint the optimal unit of time, or do enterprise clients require a 2-week engagement?
  - *Fixed Price Points*: Will domestic Indian SMEs accept a ₹1,20,000–₹2,50,000 benchmark, and will international startups accept $1,500–$3,500?
  - *Build Credit Percentage*: Does a 100% credit guarantee maximize build conversion, or should crediting be tiered based on final build contract size?
* **Next Steps**: Commercial lead to test willingness-to-pay across initial 10 inbound discovery leads before codifying fixed pricing cards.

---

### `POQ-002`: Primary AI Model Provider & Automatic Multi-Provider Failover
* **Current State**: Direct Provider SDKs and/or LiteLLM abstraction layer confirmed (`DEC-011`, `BD-015`).
* **Governance Status**: `TECHNICAL BENCHMARK REQUIRED`
* **Context**: Determining the primary LLM API provider (Anthropic Claude 3.5 Sonnet vs. OpenAI GPT-4o vs. Google Gemini 1.5 Pro) based on structured output reliability, Pydantic schema compliance, and regional API latency from India.
* **Resolution Gate**: Execute automated benchmark script testing 50 complex business problem prompts across providers during Phase 4 technical architecture.

---

### `POQ-003`: LLM Model Tiering (Frontier vs. Fast Small Models)
* **Current State**: Proposed dual-model pipeline (small model for classification; frontier model for blueprint synthesis).
* **Governance Status**: `RESEARCH REQUIRED`
* **Context**: Evaluating whether a lightweight, ultra-low-cost model (e.g. Claude 3.5 Haiku, Gemini 1.5 Flash, or GPT-4o-mini) can handle Stages 1–3 classification with $<1\%$ schema failure rate, reserving expensive frontier models strictly for Stage 5 Solution Blueprint synthesis.
* **Resolution Gate**: Benchmark extraction accuracy and token cost per discovery session.

---

### `POQ-004`: Estimation Engine Formula Calibration & Heuristic Weights
* **Current State**: Multi-vector formula defined conceptually in `06-ESTIMATION-ENGINE-SPEC.md`.
* **Governance Status**: `RESEARCH REQUIRED`
* **Context**: Sizing effort units and multiplier weights across integration complexity, user roles, and data migration.
* **Resolution Gate**: Backtest the formula against 15 past real-world custom software project scopes to calibrate upper and lower confidence bounds before live deployment.

---

### `POQ-005`: Discovery Data Retention & Purge Lifespan
* **Current State**: Compliance-ready architecture with zero model training terms (`BD-014`).
* **Governance Status**: `PROJECT OWNER DECISION REQUIRED`
* **Context**: Establishing how long anonymous vs email-gated discovery sessions remain in the local database:
  - *Option A*: Anonymous sessions purged after 14 days; email-gated dossiers retained indefinitely for client relationship continuity.
  - *Option B*: All discovery dossiers automatically purged after 90 days unless converted into an active client project.
* **Resolution Gate**: Project Owner to approve data retention policy prior to database schema implementation.

---

### `POQ-006`: Product Telemetry & Usage Analytics Depth
* **Current State**: Server-side local database event logging for MVP (`PRD-REQ-015`).
* **Governance Status**: `TBD — PHASE 3 UX & CONVERSION`
* **Context**: Determining whether to integrate a privacy-first, cookie-less open-source analytics tool (e.g. self-hosted Plausible at ₹0 cost or lightweight custom FastAPI event tables) to visualize funnel drop-off rates per diagnostic step.
* **Resolution Gate**: Finalize telemetry architecture in `docs/18-analytics/`.

---

### `POQ-007`: Session Resumption Architecture (Magic Links vs Encrypted Tokens)
* **Current State**: Proposed signed anonymous cookie elevating to magic link token in Phase 2 (`DEC-014`).
* **Governance Status**: `PROPOSED — PHASE 2 SCOPE`
* **Context**: Enabling prospective clients who leave the website during Step 3 to resume their diagnostic without starting over.
* **Resolution Gate**: Deferred to Phase 2 enhancements; linear single-session flow sufficient for MVP.

---

### `POQ-008`: Server-Side PDF Generation Technology Selection
* **Current State**: Classified as `PHASE 2` enhancement (`PRD-REQ-017`).
* **Governance Status**: `TBD — PHASE 2 SCOPE`
* **Context**: Evaluating Python-native headless HTML-to-PDF engines (WeasyPrint vs. Playwright / Chromium) for server resource efficiency on lightweight host environments.
* **Resolution Gate**: Evaluate during Phase 2 feature sprint; on-screen HTML view satisfies MVP.

---

### `POQ-009`: Self-Service Online Checkout for Discovery Sprints
* **Current State**: Strictly rejected for MVP (`PRD-MVP-002`).
* **Governance Status**: `REJECTED FOR MVP / FUTURE EVALUATION`
* **Context**: Commercial engagements require human architect review, scope ceiling validation, and custom SOW authorization (`BD-006`, `BD-010`). Self-service credit card checkout introduces severe delivery risk.

---

### `POQ-010`: Authenticated Client Portal Scope
* **Current State**: Deferred to Future Horizons (`PRD-MVP-002`, `BD-008`).
* **Governance Status**: `DEFERRED — FUTURE HORIZON`
* **Context**: Early studio engagements communicate via dedicated Slack/WhatsApp channels, shared repository access, and weekly sprint demos. Building a complex custom client portal in MVP is an unjustified engineering diversion.

---

### `POQ-011`: Production Cloud Hosting & Relational Database Decoupling
* **Current State**: Development strictly bound to Python/FastAPI/Uvicorn/MS SQL Server/SSMS locally (`BD-015`). Production database and hosting remain intentionally unfinalized.
* **Governance Status**: `TBD — PRE-DEPLOYMENT EVALUATION`
* **Context**: Evaluating Linux VPS (Docker Compose: FastAPI + Caddy + Production Relational DB) vs Managed PaaS prior to public staging launch based on flat-rate operating cost and regional Indian latency.
* **Resolution Gate**: DevOps and Technical Architect to conduct hosting evaluation in Phase 4.

---

### `POQ-012`: Multi-Language UI Support (Localization Strategy)
* **Current State**: English-first baseline for MVP.
* **Governance Status**: `PROJECT OWNER DECISION REQUIRED`
* **Context**: Evaluating whether domestic Indian SME adoption will benefit from Hindi/regional language UI toggles in future phases, or whether English satisfies 100% of business decision-makers.
* **Resolution Gate**: Project Owner to determine localization priorities following initial domestic market feedback.

---

## 4. Traceability Matrix

| Open Question ID | Topic Area | Classification | Parent Requirement |
| :--- | :--- | :--- | :--- |
| `POQ-001` | Discovery Sprint Packaging & Pricing | `HYPOTHESIS — VALIDATION REQUIRED` | `BD-004`, `BD-007` |
| `POQ-002` | Primary AI Provider & Failover | `TECHNICAL BENCHMARK REQUIRED` | `DEC-011`, `BD-015` |
| `POQ-003` | LLM Model Tiering Selection | `RESEARCH REQUIRED` | `DEC-011` |
| `POQ-004` | Estimation Formula Weights | `RESEARCH REQUIRED` | `BD-006` |
| `POQ-005` | Discovery Data Retention Limit | `PROJECT OWNER DECISION REQUIRED` | `BD-014` |
| `POQ-006` | Product Telemetry Engine | `TBD — PHASE 3 UX` | `PRD-REQ-015` |
| `POQ-007` | Session Resumption Mechanism | `PROPOSED — PHASE 2` | `DEC-014` |
| `POQ-008` | Server-Side PDF Tool Selection | `TBD — PHASE 2` | `PRD-REQ-017` |
| `POQ-009` | Online Sprint Checkout Gate | `REJECTED FOR MVP` | `BD-004`, `BD-006` |
| `POQ-010` | Dedicated Client Portal Scope | `DEFERRED — FUTURE` | `BD-008` |
| `POQ-011` | Production Hosting Decoupling | `TBD — PRE-DEPLOYMENT` | `BD-015` |
| `POQ-012` | Multi-Language Localization | `PROJECT OWNER DECISION REQUIRED` | `BD-003` |
