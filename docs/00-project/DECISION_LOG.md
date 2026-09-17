# SYSTEM DECISION LEDGER & TECHNOLOGY EVALUATION LOG (PYTHON-FIRST)
**Comprehensive Evidence-Based Evaluation of Architectural, Commercial, and Technical Choices**

---
Document Owner: Principal Project Architect & Systems Planner  
Status: FOUNDATIONAL DECISIONS RATIFIED BY OWNER (BD-001 through BD-015)  
Version: 3.1.0  
Last Updated: 2026-09-07  
Dependencies: [PROJECT_PRINCIPLES.md](file:///d:/Project_website/docs/00-project/PROJECT_PRINCIPLES.md), [TECHNOLOGY_DECISION_FRAMEWORK.md](file:///d:/Project_website/docs/00-project/TECHNOLOGY_DECISION_FRAMEWORK.md), [PYTHON_FIRST_ARCHITECTURE_EVALUATION.md](file:///d:/Project_website/docs/00-project/PYTHON_FIRST_ARCHITECTURE_EVALUATION.md)  
Related Documents: [REQUIREMENTS_REGISTER.md](file:///d:/Project_website/docs/00-project/REQUIREMENTS_REGISTER.md), [ASSUMPTIONS_REGISTER.md](file:///d:/Project_website/docs/00-project/ASSUMPTIONS_REGISTER.md)  
Ratification Status: Owner Decisions BD-001 through BD-015 are fully incorporated and binding.  
---

## 1. Decision Governance Rules

In strict adherence to the Architecture Validation Pass, the Python-First Hard Constraint, and Owner Approvals:
1. **Zero Premature Approvals**: No architectural or technology selection is marked `APPROVED` until the Project Owner provides explicit written sign-off.
2. **Owner Decision Primacy (`BD-xxx`)**: Foundational business decisions approved by the Project Owner supersede preliminary proposals and serve as the binding baseline for all subsequent phases.
3. **Hard Project Constraint (Python-First)**: The Project Owner's practical engineering expertise in Python dictates a unified Python ecosystem (FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, Jinja2/HTMX/Alpine, LiteLLM) to ensure independent maintainability.
4. **Evidence-Based Evaluation**: Every choice evaluates Free/Open-Source, Free-Tier Managed, Low Cost, and Paid options.
5. **Planning Estimates Only**: All cost figures are labeled as non-binding Planning Estimates. AI costs remain usage-dependent. Performance figures are target hypotheses to be empirically benchmarked.
6. **Permitted Statuses**: `APPROVED BY OWNER (BD-xxx)`, `CONFIRMED (CST-CNF-xxx)`, `PROPOSED`, `DECISION REQUIRED`, `REJECTED`, `DEFERRED`, `SUPERSEDED`.

---

## 2. Summary Status Table

| ID | Domain | Topic | Candidates Evaluated | Selected / Approved Option | Status | Owner Decision Ref |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`DEC-001`** | Brand | Official Brand Name & Domain Identity | Codename Parameterization vs Immediate Legal Name | Parameterized working title `[STUDIO_NAME]` until domain/trademark finalized | `APPROVED BY OWNER` | `BD-001` |
| **`DEC-002`** | Business | Commercial Model & Discovery Monetization | Free Diagnostic $\rightarrow$ Paid Sprint vs Free Consulting vs Hard Paywall | Free AI Diagnostic $\rightarrow$ Paid Discovery Sprint (Pricing TBD) | `APPROVED BY OWNER` | `BD-004` |
| **`DEC-003`** | Business | Geographic Launch & Market Strategy | India-first vs Pure Global vs Global Day 1 | India-first with planned expansion toward Global; no invented launch date | `APPROVED BY OWNER` | `BD-003` |
| **`DEC-004`** | Product | AI Discovery Lead Gating Model | Progressive Reveal vs Upfront Gate vs 100% Ungated | Value-First Progressive Reveal (ungated exploration, email for deep outputs)| `APPROVED BY OWNER` | `BD-005` |
| **`DEC-005`** | Product | AI Discovery Interface Paradigm | Guided Stepper + HTMX/Alpine vs Pure Chat vs Static Form | Guided Adaptive Stepper (HTMX + Alpine.js); Primary CTA: *"Start With Your Problem"* | `CONFIRMED` | `BD-012`, `BD-015` |
| **`DEC-006`** | Product | Estimation Engine Output Disclosure | Indicative Ranges + Disclaimers vs Concealed vs Exact Price | Indicative Budget & Timeline Ranges; Non-Binding Disclaimers; Human SOW Req. | `APPROVED BY OWNER` | `BD-006` |
| **`DEC-007`** | Tech | Frontend Architecture (Python-Compatible) | Jinja2 + HTMX + Alpine vs Jinja2 + Vanilla JS vs React/Vite | Jinja2 + HTMX (~14KB) + Alpine.js (~15KB) + Modern CSS Design Tokens | `CONFIRMED` | `BD-015` |
| **`DEC-008`** | Tech | Backend Framework & Dev Server | FastAPI + Uvicorn (--reload) vs Flask vs Django | FastAPI (Python 3.12+ ASGI) + local Uvicorn (₹0 infrastructure cost) | `CONFIRMED BY OWNER`| `BD-015` |
| **`DEC-009`** | Tech | Database Engine (Dev vs Prod) | Dev: MS SQL Server + SSMS; Prod: Evaluated Later | Dev: Microsoft SQL Server + SSMS via SQLAlchemy; Prod: Open / Decoupled | `CONFIRMED BY OWNER`| `BD-015` |
| **`DEC-010`** | DevOps | Compute & Hosting Infrastructure | Dev: Local Machine (₹0); Prod: VPS vs PaaS vs AWS | Dev: Local Machine (₹0); Prod: Decoupled & Undecided (To Be Evaluated Later) | `CONFIRMED BY OWNER`| `BD-015` |
| **`DEC-011`** | AI | AI Model Libraries & Framework | Direct Provider SDKs / LiteLLM + Pydantic v2 vs LangChain | Direct SDKs / LiteLLM + Pydantic v2 Structured Outputs (Python-First) | `CONFIRMED` | `BD-010`, `BD-015` |
| **`DEC-012`** | AI | Knowledge Base & Solution Templates | In-Memory Python Dicts (MVP) $\rightarrow$ `pgvector` (Phase 2) | In-Memory Curated Python Catalog for MVP at ₹0 cost | `CONFIRMED` | `BD-015` |
| **`DEC-013`** | Security | Discovery Data Privacy & Compliance | Zero-Retention Enterprise API + Python PII Masking | Zero-Retention API Terms + PII Scrubber; Privacy Best Practices (No unverified certs)| `APPROVED BY OWNER` | `BD-014` |
| **`DEC-014`** | Security | User Authentication & Session Continuity | Anonymous Cookie $\rightarrow$ Magic Link Token (FastAPI) | Anonymous UUID Cookie $\rightarrow$ Magic Link Elevation (FastAPI native) | `CONFIRMED` | `BD-005`, `BD-015` |
| **`DEC-015`** | Operations| Human-in-the-Loop Proposal SLA | 24h Proposed Internal Target vs 48h-72h vs Legal SLA | Internal Response-Time Target Policy; No Public Contractual SLA Guarantee | `APPROVED BY OWNER` | `BD-013` |

---

## 3. Owner-Approved Business Decisions Register (`BD-001` through `BD-015`)

The Project Owner has explicitly reviewed, ratified, and authorized the following foundational business decisions as binding baselines for Phase 1 and all downstream documentation:

### `BD-001` — Brand Identity Placeholder
* **Approved Decision**: `[STUDIO_NAME]` remains the canonical working placeholder across all documentation, UI mocks, schemas, and templates until legal trademark, corporate incorporation, and primary domain checks are separately finalized.
* **Governing Rule**: Do NOT select or assume an unapproved brand name.

### `BD-002` — Target Customer Segments
* **Approved Decision**: Primary target customers are formally defined as:
  1. **Startups** (Pre-seed to Series A, building first software or launching MVP).
  2. **SMEs** (Established non-tech and tech businesses seeking automation and efficiency).
  3. **Growing Businesses** (Mid-market enterprises hitting legacy technology ceilings).
* **Governing Rule**: Do NOT invent demographic statistics, total addressable market counts, or unverified market share metrics.

### `BD-003` — Geographic Sequencing & Launch Strategy
* **Approved Decision**: Commercial focus is **India-first** with an intentional, architected pathway toward **global customers**.
* **Governing Rule**: Do NOT invent a premature launch date. Maintain dual-currency readiness (INR/USD) without forcing immediate international registration.

### `BD-004` — Discovery Monetization Architecture
* **Approved Decision**: Commercial discovery follows a two-tier model:
  1. **Free AI Diagnostic**: Interactive self-service assessment producing an Executive Opportunity Map.
  2. **Paid Discovery Sprint**: Dedicated architectural engagement for qualified, high-intent prospects, with packaging, duration, pricing, and crediting terms to be validated.
* **Governing Rule**: Do NOT invent final paid Discovery Sprint pricing figures. Packaging, duration, pricing, and commercial crediting remain TBD until validated (`HYPOTHESIS — VALIDATION REQUIRED`).

### `BD-005` — Lead Capture & Gating Governance
* **Approved Decision**: Value-first experience. Basic exploration, question answering, and high-level problem translation do NOT require mandatory account creation or upfront gating. Contact information (corporate email, WhatsApp/phone) is requested only to unlock deeper, proprietary outputs (detailed Solution Blueprint, indicative budget ranges, downloadable specifications).
* **Governing Rule**: Maximize top-of-funnel diagnostic completion by never placing hard registration walls in front of initial insight.

### `BD-006` — Estimation Transparency & Non-Binding Disclaimers
* **Approved Decision**: The website and diagnostic engine may provide:
  - Indicative budget range (low to high bands).
  - Indicative timeline (estimated weeks/months).
  - Complexity and technical effort signals.
* **Mandatory Legal Disclaimer**: Every automated output must clearly and prominently state that **estimates are indicative planning ranges and NOT binding commercial quotations**. Final commercial scope and binding Statements of Work (SOW) strictly require human architect review.

### `BD-007` — Market Pricing Position
* **Approved Decision**: The studio occupies a **Mid-Market $\rightarrow$ Premium** pricing position, reflecting high-craft, senior architectural oversight, and production-grade software delivery.
* **Governing Rule**: Do NOT invent fixed service prices, hourly rate cards, or off-the-shelf packages unless separately approved.

### `BD-008` — Strategic Business Evolution Ladder
* **Approved Decision**: The long-term commercial trajectory of `[STUDIO_NAME]` progresses through five deliberate stages:
  $$\text{Services} \longrightarrow \text{Reusable Technology} \longrightarrow \text{Productized Solutions} \longrightarrow \text{SaaS} \longrightarrow \text{Technology Products}$$
* **Governing Rule**: This is a strategic long-term trajectory. Do NOT claim that all five stages currently exist or are commercially active.

### `BD-009` — Studio Market Positioning
* **Approved Decision**: The company is positioned as an **AI-Native Technology Studio & Systems Partner**. It is NOT positioned as an "AI-only company" or a wrapper tool. AI is a core engineering and discovery multiplier, but the core business is turning business problems into working, durable technology assets.

### `BD-010` — Human + AI Collaboration Law
* **Approved Decision**: The fundamental operating doctrine is:
  > **"AI handles leverage. Humans handle judgement."**
* **Human Responsibility Mandate**: Humans retain exclusive, non-delegable responsibility for:
  - Business judgement and commercial negotiations.
  - Architecture sign-off and system design approval.
  - Product strategy decisions.
  - Security, privacy, and regulatory sign-offs.
  - Quality assurance and release gatekeeping.
  - Client relationships and stakeholder management.
  - Final proposals and Statements of Work.
  - Final production delivery and launch decisions.

### `BD-011` — Core Brand Promise & Guiding Philosophy
* **Approved Decision**:
  - **Core Promise**: *"We turn business problems into technology."*
  - **Guiding Philosophy**: *"Technology should adapt to the business — not the business to technology."*
  - **North Star**: Understand the business $\rightarrow$ Translate the problem $\rightarrow$ Build what matters $\rightarrow$ Automate what shouldn't be manual $\rightarrow$ Scale what works.

### `BD-012` — Primary Call-to-Action (CTA)
* **Approved Decision**: The primary website and marketing CTA is:
  > **"Start With Your Problem"**
* **Governing Rule**: The CTA anchors a problem-first, consultative entry point rather than a feature-centric or product-demo prompt.

### `BD-013` — Service Level Agreements (SLA)
* **Approved Decision**: **No public contractual SLA is guaranteed initially.** An internal operational target (e.g., 24 business hours for proposal reviews) may exist for operational discipline, but must NOT be presented to clients as a legally binding guarantee with financial penalties.

### `BD-014` — Legal, Privacy & Compliance Language
* **Approved Decision**: Documentation and marketing must use **compliance-ready, privacy-respecting, and security-best-practice language**.
* **Governing Rule**: Do NOT make formal statutory certifications (e.g., "SOC 2 Type II Certified", "HIPAA Compliant", "ISO 27001 Certified") without actual independent legal and third-party audit verification.

### `BD-015` — Development Architecture & Infrastructure Baseline
* **Approved Decision**:
  - **Backend Language & Framework**: Python 3.12+ with FastAPI (Python-first hard constraint).
  - **Development Application Server**: Uvicorn locally (`--reload`).
  - **Development Database**: Microsoft SQL Server (Developer/Express Edition) managed via SQL Server Management Studio (SSMS), accessed via SQLAlchemy 2.x and Alembic.
  - **Development Infrastructure Target**: **₹0 infrastructure cost** running entirely on local developer workstations.
  - **Frontend Architecture**: Jinja2 server-side rendering + HTMX + Alpine.js + Modern Vanilla CSS.
  - **Production Hosting & Database**: **Remains intentionally unfinalized, open, and decoupled**; to be evaluated prior to public deployment.

---

## 4. Evidence-Based Decision Evaluations (Detailed Records)

---

### `DEC-001`: Official Brand Name & Domain Identity
* **Status**: `APPROVED BY OWNER (BD-001)`
* **Approved Selection**: Use parameterized working placeholder `[STUDIO_NAME]` across all docs, templates, and schemas until legal checks and domain registrations are executed.
* **Why Ratified**: Eliminates dependency blocking on brand naming; enables 100% completion of foundational business, UX, and technical architecture without rework.

---

### `DEC-002`: Commercial Model & Discovery Monetization
* **Status**: `APPROVED BY OWNER (BD-004)`
* **Approved Selection**: **Freemium AI Diagnostic $\rightarrow$ Paid Discovery Sprint**. Interactive diagnostic yields an Executive Opportunity Map; comprehensive architectural solution design offered as a paid sprint, with commercial packaging, duration, pricing, and crediting terms to be validated.
* **Why Ratified**: Provides high top-of-funnel lead velocity while disqualifying non-serious tire-kickers before committing expensive senior architect time. Sprint duration, pricing, and crediting terms remain TBD until validated.

---

### `DEC-003`: Geographic Launch Sequence & Market Strategy
* **Status**: `APPROVED BY OWNER (BD-003)`
* **Approved Selection**: **India-first $\rightarrow$ Global Expansion**. Target domestic Indian founders, SMEs, and growth businesses first; design architecture with multi-currency and cross-border capabilities for global reach.
* **Why Ratified**: Capitalizes on rapid Indian digital transformation while establishing international engineering standards. No premature public launch date is committed.

---

### `DEC-004`: AI Discovery Lead Capture Gating Model
* **Status**: `APPROVED BY OWNER (BD-005)`
* **Approved Selection**: **Value-First Progressive Reveal**. Complete diagnostic flow is ungated; high-level problem translation and Opportunity Map are shown immediately; deep Blueprint and indicative estimates require corporate email.
* **Why Ratified**: Delivers immediate reciprocal value before asking for contact details, maximizing conversion and reducing funnel abandonment.

---

### `DEC-005`: AI Discovery Interface Paradigm
* **Status**: `CONFIRMED (BD-012, BD-015)`
* **Approved Selection**: **Guided Adaptive Stepper (HTMX + Alpine.js)** centered around primary CTA *"Start With Your Problem"*. Five focused steps: Industry $\rightarrow$ Core Problem $\rightarrow$ Tech Maturity $\rightarrow$ Urgency $\rightarrow$ Synthesis.
* **Why Ratified**: Combines structured low-friction inputs with dynamic contextual adaptation, preventing the open-ended "blank box" paralysis of pure chat interfaces.

---

### `DEC-006`: Estimation Engine Transparency & Output Disclosure
* **Status**: `APPROVED BY OWNER (BD-006)`
* **Approved Selection**: **Confidence-Banded Indicative Ranges with Mandatory Disclaimers**. Automated algorithm outputs low-to-high budget bands and timeline ranges with an explicit disclaimer that formal quotes require human architect review.
* **Why Ratified**: Qualifies customer budget expectations transparently while protecting the business from binding scope liabilities.

---

### `DEC-007`: Frontend Architecture (Compatible with Python/FastAPI)
* **Status**: `CONFIRMED (BD-015)`
* **Approved Selection**: **FastAPI + Jinja2 + HTMX (~14KB) + Alpine.js (~15KB) + Modern Vanilla CSS Design Tokens**.
* **Why Ratified**: Eliminates Node.js build pipelines; preserves single-language Python ecosystem; provides server-driven SPA-like reactivity; guarantees perfect SEO crawlability and sub-second load times.

---

### `DEC-008`: Backend Framework & Development Server Core
* **Status**: `CONFIRMED BY OWNER (BD-015)`
* **Approved Selection**: **FastAPI (Python 3.12+) Modular Monolith** served locally via **Uvicorn** (`--reload`) at **₹0 infrastructure cost**.
* **Why Ratified**: Aligns with Project Owner's proven Python expertise; provides asynchronous non-blocking performance for streaming LLM tokens; Pydantic v2 validation; automatic OpenAPI documentation.

---

### `DEC-009`: Database Engine & Persistence (Development vs. Production)
* **Status**: `CONFIRMED BY OWNER (BD-015)`
* **Approved Selection**:
  - **Development Database**: **Microsoft SQL Server (Developer / Express Edition)** managed via **SQL Server Management Studio (SSMS)**.
  - **ORM & Migrations**: SQLAlchemy 2.x (`aioodbc` / `pyodbc`) + Alembic.
  - **Dev Cost**: **₹0 infrastructure cost**.
  - **Production Database**: **Intentionally Decoupled & Open** (to be evaluated prior to production deployment based on scalability, cloud cost, and operational requirements).
* **Why Ratified**: Leverages Project Owner's direct practical experience with SQL Server and SSMS for fast local schema iteration, visual inspection, and debugging without introducing extraneous development tooling.

---

### `DEC-010`: Compute & Hosting Infrastructure (Development vs. Production)
* **Status**: `CONFIRMED BY OWNER (BD-015)`
* **Approved Selection**:
  - **Development Compute**: Local developer workstation running Uvicorn at **₹0 infrastructure cost**.
  - **Production Hosting**: **Decoupled and Undecided**; to be evaluated later (e.g. Linux VPS via Docker Compose vs Managed PaaS).
* **Why Ratified**: Ensures development begins immediately with zero overhead while preserving complete architectural flexibility for production deployment.

---

### `DEC-011`: AI Model Libraries & Framework Selection
* **Status**: `CONFIRMED (BD-010, BD-015)`
* **Approved Selection**: **Direct Provider SDKs (`google-genai`, `anthropic`, `openai`) and/or LiteLLM + Pydantic v2 Structured Outputs**.
* **Why Ratified**: Avoids heavyweight, unstable agent framework abstractions (LangChain/CrewAI); provides robust type-safe validation and clean failover logic.

---

### `DEC-012`: Knowledge Retrieval & Solution Template Search
* **Status**: `CONFIRMED (BD-015)`
* **Approved Selection**: **In-Memory Curated Python Dictionary Catalog (30–50 templates) with tag-based heuristic scoring** for MVP at ₹0 cost.
* **Why Ratified**: Instantaneous lookup, zero external vector database infrastructure overhead, deterministic reproducibility.

---

### `DEC-013`: Client Discovery Data Privacy & Compliance Safeguards
* **Status**: `APPROVED BY OWNER (BD-014)`
* **Approved Selection**: **Zero-Training Enterprise API Terms + Automated Python PII Masking**. Compliance-ready and privacy-by-design posture without claiming unverified statutory certifications.
* **Why Ratified**: Protects customer confidentiality and safeguards intellectual property while strictly adhering to owner decision `BD-014`.

---

### `DEC-014`: User Authentication & Discovery Session Continuity
* **Status**: `CONFIRMED (BD-005, BD-015)`
* **Approved Selection**: **Anonymous UUID Cookie $\rightarrow$ Magic Link Email Elevation** implemented natively in FastAPI with signed cryptographic tokens.
* **Why Ratified**: Frictionless value-first diagnostic entry without forcing upfront password accounts; zero paid third-party authentication dependencies ($0/mo).

---

### `DEC-015`: Human-in-the-Loop Proposal SLA Policy
* **Status**: `APPROVED BY OWNER (BD-013)`
* **Approved Selection**: **Internal Operational Target (24 Business Hours) without Public Contractual SLA Guarantee**.
* **Why Ratified**: Drives internal operational excellence without exposing the studio to commercial or legal breach liabilities during early-stage operations.

---

## 5. Traceability to Downstream Documentation

All approved decisions are enforced across the project documentation tree:
- **Phase 1 (Business)**: Reflects `BD-001` through `BD-015` as foundational assumptions and business requirements (`docs/01-business/`).
- **Phase 2 (Brand & Product)**: Will parameterize `[STUDIO_NAME]` (`BD-001`), embody primary CTA *"Start With Your Problem"* (`BD-012`), and design the Guided Stepper (`BD-005`).
- **Phase 3 (Website & UX)**: Will implement HTMX/Alpine progressive reveal components (`BD-005`, `BD-006`, `BD-015`).
- **Phase 4 (Technical Architecture)**: Will specify FastAPI, MS SQL Server dev environment, Uvicorn local runner, and decoupled production infrastructure (`BD-015`).
