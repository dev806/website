# Product Requirements Register (PRD Specifications)

**Document ID:** `DOC-PRD-011`  
**Classification:** Product Specification / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001) through [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Requirements Register](file:///d:/Project_website/docs/00-project/REQUIREMENTS_REGISTER.md) | [MVP Scope](file:///d:/Project_website/docs/03-product/08-MVP-SCOPE.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Canonical Product Requirements Register

---

## 1. Executive Summary & Governance Rules

This register establishes the authoritative catalog of product-level functional, user experience, and operational requirements for the `[STUDIO_NAME]` platform and its signature **AI Project Discovery Engine**.

### Requirements Governance Rules:
1. **Immutable Identifiers**: Every requirement is bound to a unique `PRD-REQ-xxx` identifier.
2. **MoSCoW Prioritization**: Categorized strictly as **Must Have (P0)**, **Should Have (P1)**, or **Could Have (P2)**.
3. **Lifecycle Partitioning**: Explicitly designated as **MVP**, **Phase 2**, or **Future Horizon**.
4. **Zero Speculative Requirements**: Every requirement traces directly to an owner-approved decision (`BD-*`), business requirement (`BR-*`), or customer requirement (`CR-*`).

---

## 2. Product Requirements Register (`PRD-REQ-xxx`)

| Req ID | Requirement Statement | Strategic Rationale | Priority | Horizon | Source Ref | Validation Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`PRD-REQ-001`** | **Primary Problem Intake**: Provide a prominent, accessible input allowing users to describe business friction in natural language without jargon. | Core philosophy: *"Technology should adapt to the business"*. Eliminates specification paralysis. | **Must** | **MVP** | `BD-011`, `BD-012` | `APPROVED` | None |
| **`PRD-REQ-002`** | **Adaptive 4-Step Questionnaire**: Present four structured contextual steps (Scale, Tech State, Bottleneck, Urgency) via interactive pill selectors. | Low cognitive load on mobile; captures essential architectural boundary signals. | **Must** | **MVP** | `BD-015`, `CR-CUST-002` | `APPROVED` | `PRD-REQ-001` |
| **`PRD-REQ-003`** | **Dynamic HTMX Fragment Swaps**: Stepper transitions and content reveals must execute via server-rendered HTML partials with zero full-page reloads. | Fast sub-second response, zero Node.js build complexity, single-language maintainability. | **Must** | **MVP** | `BD-015`, `DEC-007` | `CONFIRMED` | FastAPI, HTMX |
| **`PRD-REQ-004`** | **Client-Side PII Scrubbing**: Middleware must automatically detect and sanitize personal phone numbers, bank details, and passwords before prompt assembly. | Ensures strict enterprise data privacy and prevents sensitive leakage to external LLM APIs. | **Must** | **MVP** | `BD-014`, `DEC-013` | `APPROVED` | Python scrubber |
| **`PRD-REQ-005`** | **Pydantic Schema Validation**: All LLM synthesis responses must strictly parse into typed Pydantic v2 schemas with automated validation retry. | Guarantees deterministic, bug-free rendering of downstream UI components. | **Must** | **MVP** | `BD-015`, `DEC-011` | `CONFIRMED` | Pydantic v2 |
| **`PRD-REQ-006`** | **Ungated Opportunity Map**: Display an instant Executive Opportunity Map (Root Causes, Categorized Tags, Complexity) without requiring email or login. | Value-first philosophy; proves diagnostic competence before asking for commercial credentials. | **Must** | **MVP** | `BD-005`, `PRD-VIS-004` | `APPROVED` | `PRD-REQ-005` |
| **`PRD-REQ-007`** | **Categorized Opportunity Tags**: Classify identified interventions across five standardized categories (Automation, AI, Build, Integrate, Scale). | Standardizes scoping taxonomy across client domains and studio service pillars. | **Must** | **MVP** | `BD-009`, `BR-SRV-001` | `APPROVED` | `PRD-REQ-006` |
| **`PRD-REQ-008`** | **Value-Gated Blueprint Access**: Unlocking the detailed 18-section Solution Blueprint and budget estimates requires Work Email, Name, and Company. | High top-of-funnel conversion while capturing qualified enterprise contact details. | **Must** | **MVP** | `BD-005`, `BA-MOD-001` | `APPROVED` | `PRD-REQ-006` |
| **`PRD-REQ-009`** | **18-Section Solution Blueprint**: Render an architectural specification detailing recommended approach, functional user flows, data models, and risks. | Provides tangible systems architecture specifications that clients own completely. | **Must** | **MVP** | `BD-011`, `PRD-BLU-003` | `APPROVED` | `PRD-REQ-008` |
| **`PRD-REQ-010`** | **AI vs Human Content Badging**: Prominently badge automated blueprints as `[AI-GENERATED DRAFT]` and distinguish them from human-certified SOWs. | Preserves absolute trust and enforces the doctrine: *"AI handles leverage. Humans handle judgement."* | **Must** | **MVP** | `BD-010`, `PRD-BLU-002` | `APPROVED` | `PRD-REQ-009` |
| **`PRD-REQ-011`** | **Indicative Estimation Engine**: Calculate algorithmic budget and timeline bands derived from multi-vector complexity signals without hard-coded numbers. | Qualifies client budget expectations transparently without creating legal quotation liability. | **Must** | **MVP** | `BD-006`, `BD-007` | `APPROVED` | `PRD-REQ-005` |
| **`PRD-REQ-012`** | **Mandatory Legal Disclaimer**: Every automated estimate must prominently display the non-binding planning disclaimer notice. | Legal protection; prevents automated figures from being misconstrued as binding commercial bids. | **Must** | **MVP** | `BD-006`, `PRD-EST-001` | `APPROVED` | `PRD-REQ-011` |
| **`PRD-REQ-013`** | **Dual-Currency Localization**: Display budget bands dynamically in INR (₹) for domestic Indian visitors and USD ($) for international visitors. | Optimizes commercial alignment across target geographies without currency friction. | **Should**| **MVP** | `BD-003`, `DEC-003` | `APPROVED` | Geo-IP routing |
| **`PRD-REQ-014`** | **Architect Lead Dossier Dispatch**: Automated background event compiling raw prompt, tags, blueprint, and bands into an internal notification dossier. | Empowers human Principal Architects to review submissions within internal 24-hour target. | **Must** | **MVP** | `BD-010`, `BD-013` | `APPROVED` | SMTP / Webhook |
| **`PRD-REQ-015`** | **Privacy-First Telemetry**: Log server-side diagnostic completion events and drop-off steps without third-party tracking cookies or personal data. | Informs funnel optimization while maintaining complete compliance with global privacy standards. | **Must** | **MVP** | `BD-014`, `PRD-STR-007` | `APPROVED` | Local DB logging|
| **`PRD-REQ-016`** | **Local-First Zero-Cost Dev**: Entire application and database must run locally on developer workstations at ₹0 infrastructure cost. | Aligns with owner development constraints and eliminates premature cloud hosting burn. | **Must** | **MVP** | `BD-015`, `DEC-008` | `CONFIRMED` | SQL Server/SSMS |
| **`PRD-REQ-017`** | **Downloadable PDF Blueprint**: Compile on-screen Solution Blueprint into a presentation-ready branded PDF download for stakeholders. | High utility for enterprise champions presenting proposals to executive leadership. | **Should**| **Phase 2**| `DEC-005` | `PROPOSED` | Headless PDF |
| **`PRD-REQ-018`** | **Anonymous Magic Link Resumption**: Issue encrypted signed tokens allowing users to resume in-progress discovery sessions across devices. | Reduces abandonment for users interrupted during diagnostic exploration without requiring passwords. | **Should**| **Phase 2**| `DEC-014` | `PROPOSED` | FastAPI tokens |
| **`PRD-REQ-019`** | **Interactive Budget Sliders**: Provide interactive Alpine.js sliders enabling users to add/remove capabilities and observe timeline impacts. | Enhances user engagement and self-education regarding software complexity trade-offs. | **Could** | **Phase 2**| `BD-006` | `PROPOSED` | Alpine.js |
| **`PRD-REQ-020`** | **Internal Admin Review Portal**: Dedicated web UI for studio architects to inspect, filter, calibrate, and respond to incoming lead dossiers. | Streamlines internal proposal authoring workflows as weekly diagnostic volume expands. | **Should**| **Phase 2**| `BD-015` | `PROPOSED` | FastAPI Admin |
| **`PRD-REQ-021`** | **Multi-Tenant Enterprise Portal**: Self-service accounts for corporate IT teams to conduct continuous project discovery across departments. | Foundation for long-term commercial software productization (SaaS evolution). | **Could** | **Future** | `BD-008` | `HYPOTHESIS` | Multi-Tenant DB |
| **`PRD-REQ-022`** | **Blueprint-to-Code Compiler**: Automated engine generating initial FastAPI schemas and Alembic migrations directly from approved blueprints. | Institutionalizes studio engineering velocity into an autonomous proprietary technology product. | **Could** | **Future** | `BD-008` | `HYPOTHESIS` | Code generator |

---

## 3. Traceability to Business Decisions (`BD-*`)

```text
BD-001 (Brand Placeholder)      ──► PRD-REQ-001, PRD-REQ-009
BD-002 (Target Customers)       ──► PRD-REQ-002, PRD-REQ-007
BD-003 (Geography & Currency)   ──► PRD-REQ-013
BD-004 (Discovery Monetization) ──► PRD-REQ-006, PRD-REQ-008
BD-005 (Lead Capture Gating)    ──► PRD-REQ-006, PRD-REQ-008
BD-006 (Indicative Estimation)  ──► PRD-REQ-011, PRD-REQ-012, PRD-REQ-019
BD-007 (Pricing Position)       ──► PRD-REQ-011
BD-008 (Business Evolution)     ──► PRD-REQ-021, PRD-REQ-022
BD-009 (Studio Positioning)     ──► PRD-REQ-001, PRD-REQ-007
BD-010 (Human + AI Duality)     ──► PRD-REQ-010, PRD-REQ-014
BD-011 (Core Promise)           ──► PRD-REQ-001, PRD-REQ-009
BD-012 (Primary CTA)            ──► PRD-REQ-001
BD-013 (Internal SLA Target)    ──► PRD-REQ-014
BD-014 (Privacy & Compliance)   ──► PRD-REQ-004, PRD-REQ-015
BD-015 (Python-First Dev Stack) ──► PRD-REQ-003, PRD-REQ-005, PRD-REQ-016
```

---

## 4. Requirement Verification & Acceptance Criteria

Every requirement in this register must satisfy three acceptance criteria before being marked `VERIFIED`:

1. **Automated Unit / Integration Test**: Verifiable via automated Pytest suites running locally against Microsoft SQL Server (`BD-015`).
2. **Deterministic Schema Conformance**: JSON inputs and outputs must strictly validate against Pydantic schemas without runtime type errors.
3. **Audit Compliance**: Free from unverified marketing claims, unbacked metrics, or contractual SLA guarantees.
