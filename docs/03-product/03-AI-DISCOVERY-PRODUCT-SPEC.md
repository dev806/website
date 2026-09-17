# AI Project Discovery System: Product Specification

**Document ID:** `DOC-PRD-003`  
**Classification:** Product Specification / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-011](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-011), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Product Vision](file:///d:/Project_website/docs/03-product/01-PRODUCT-VISION.md) | [Product Strategy](file:///d:/Project_website/docs/03-product/02-PRODUCT-STRATEGY.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Canonical Product Specification

---

## 1. Executive Summary & Experience Flow

The **AI Project Discovery System** is the signature interactive capability of the `[STUDIO_NAME]` platform, triggered by the universal primary call-to-action: **"Start With Your Problem"** (`BD-012`).

It guides prospective clients through a six-stage consultative journey—converting unstructured business friction into an **Executive Opportunity Map**, a comprehensive **Technical Solution Blueprint**, and a **Confidence-Banded Indicative Planning Range** with zero upfront commercial pressure.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE SIX STAGES OF THE DISCOVERY ENGINE                          │
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│ Stage 1: Problem  │ Plain-language intake of operational pain and business objectives  │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Stage 2: Questions│ Adaptive, low-friction structured choices refining scope & maturity│
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Stage 3: Context  │ Pydantic normalization into a validated structured business dossier│
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Stage 4: Map      │ Real-time Opportunity Map (Bottlenecks, Automation, AI, Risks)     │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Stage 5: Blueprint│ Detailed Solution Blueprint (Architecture, Capabilities, Data, Ops)│
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Stage 6: Estimate │ Indicative budget and timeline bands with non-binding disclaimers  │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Business Problem Ingestion

* **User Objective**: Articulate what they want to achieve or where operational friction is hurting the business, speaking in their natural business vocabulary.
* **UI Presentation**:
  - A clean, distraction-free modal or dedicated page view.
  - Prominent prompt header: *"What business problem or goal are you trying to solve?"*
  - Expandable text input with dynamic placeholder suggestions tailored by role (e.g. *"We want to build a custom client portal to eliminate manual WhatsApp order tracking"*, *"We need an MVP to validate our fintech idea with angel investors"*).
  - High-level industry sector selector (Logistics, Healthcare, Professional Services, Retail/E-commerce, Manufacturing, SaaS/Tech, Other).
* **System Actions**:
  - Client-side input sanitization via Alpine.js (checking for reasonable prompt length, stripping HTML tags).
  - PII scrubbing pass removing personal phone numbers, bank details, or passwords before sending text to the LLM (`BD-014`).
  - Asynchronous background request to FastAPI backend (`POST /api/v1/discovery/ingest`).

---

## 3. Stage 2: Adaptive Structured Questions

* **User Objective**: Provide essential contextual constraints without getting bogged down in endless interrogation.
* **UI Presentation**:
  - A 4-step progressive stepper with visual progress indicators (Step 1 to 4).
  - Interactive pill selectors (multi-select and single-select) requiring minimal typing on mobile devices.
  - Step categories:
    1. **Organizational Scale**: Solo Founder / 2–10 Employees / 11–50 Employees / 51–200 Employees / 200+ Enterprise.
    2. **Current Technical State**: Manual Spreadsheets & WhatsApp (Level 1) / Disconnected SaaS Tools (Level 2) / Aging Legacy Monolith (Level 3) / Modern Tech needing AI (Level 4).
    3. **Primary Bottleneck**: Manual Data Entry / Disconnected Systems / Slow Customer Response / High Software Costs / No Developer Bandwidth.
    4. **Desired Horizon & Urgency**: Immediate Relief (< 1 Month) / Standard Quarter (1–3 Months) / Strategic Roadmap (3–6 Months).
* **System Actions**:
  - HTMX dynamic fragment swaps updating stepper state seamlessly without full-page reloads (`BD-015`).
  - Session state maintained in signed anonymous cookies (`DEC-014`).

---

## 4. Stage 3: Structured Context Normalization

* **User Objective**: Experience an instantaneous, intelligent synthesis of their inputs.
* **UI Presentation**:
  - A brief, polished animated loading state (1.5 to 2.5 seconds) displaying purposeful status indicators:
    * *"Deconstructing operational pain points..."*
    * *"Evaluating reusable architectural patterns..."*
    * *"Synthesizing Executive Opportunity Map..."*
* **System Actions (FastAPI Backend)**:
  - Validates combined user inputs against a strictly typed `DiscoveryContext` Pydantic v2 schema.
  - Executes a single structured output prompt via LiteLLM / provider SDK using zero-retention commercial API terms (`BD-014`).
  - Normalizes the response into standardized domain entities: Problem Category, Impact Severity, Automation Potential, Integration Surface, Risk Signals, and Unknown Variables.

---

## 5. Stage 4: The Executive Opportunity Map (Ungated)

* **User Objective**: View an immediate, structured analysis of their problem—proving that the studio understands their business reality before asking for contact info (`BD-005`).
* **UI Presentation**:
  - **Identified Core Bottlenecks**: Summary of root operational friction distinguished from surface symptoms.
  - **High-Leverage Opportunity Tags**: Visual badges highlighting opportunities across:
    * *Workflow Automation* (e.g. *"Automated Invoice Extraction"*)
    * *AI Capability* (e.g. *"Conversational Lead Qualifier"*)
    * *System Integration* (e.g. *"Unified CRM-to-ERP Sync"*)
  - **Technical Complexity Signal**: Low / Medium / High / Architectural Overhaul.
  - **The Value-First Reveal Barrier**: High-level map is 100% visible on screen; an explicit callout invites the user to unlock the complete **Technical Solution Blueprint** and **Indicative Budget/Timeline Bands** by providing their corporate work email.

---

## 6. Stage 5: The Technical Solution Blueprint (Value-Gated)

* **User Objective**: Receive a comprehensive, actionable systems engineering specification tailored to their problem.
* **Access Gate**: User inputs Work Email + Name + Company Name. (Phone / WhatsApp is optional).
* **Blueprint Structure**:
  1. **Executive Summary**: Business objective, core transformation, and expected operational outcome.
  2. **Recommended Architectural Approach**: Modular monolith architecture, language recommendations (Python/FastAPI), relational data modeling, and frontend strategy.
  3. **Functional Capabilities Matrix**: Core user flows and administrative capabilities required.
  4. **AI & Automation Specifications**: Exact prompt pipelines, RAG document indexing, or event-driven webhook triggers.
  5. **System Integrations**: Required third-party APIs (payment gateways, WhatsApp Business, CRMs, ERPs).
  6. **Data & Security Guardrails**: Encryption standards, PII masking rules, backup strategies, and role-based access control.
  7. **Assumptions & Unknowns**: Explicit list of technical unknowns that require human architect discovery.

---

## 7. Stage 6: Indicative Estimation & Human Review Gate

* **User Objective**: Understand the realistic planning parameters (investment range and timeline) without getting locked into deceptive quotes.
* **UI Presentation**:
  - **Indicative Budget Range**: Confidence-banded planning investment (e.g. Low Band to High Band in INR or USD based on user locale).
  - **Indicative Timeline Range**: Estimated calendar weeks to production deployment (e.g. 4 to 8 weeks).
  - **Complexity & Confidence Breakdown**: Visual uncertainty meter explaining what variables drive the range (e.g. integration API stability, legacy data migration volume).
* **Mandatory Legal Disclaimer Notice (`BD-006`)**:
  > **IMPORTANT NOTICE: Indicative Planning Range Only**  
  > *The budget and timeline ranges presented here are algorithmic planning estimates generated to qualify technical scope and align commercial expectations. They do NOT constitute a binding quotation or commercial contract. Final scope, system architecture, and binding Statements of Work (SOW) strictly require human Principal Architect review.*
* **The Human Gate Action Button**:
  - **Primary Action**: **"Request Principal Architect Review"** (`BD-010`).
  - Submits the complete diagnostic dossier to the studio's internal engineering review board, triggering our internal 24-business-hour response protocol (`BD-013`).

---

## 8. Traceability Matrix

| Requirement ID | Product Spec Dimension | Section Reference | Decision Reference |
| :--- | :--- | :--- | :--- |
| `PRD-DIS-001` | Six-stage conceptual discovery engine lifecycle | Section 1 | `BD-011`, `BD-012` |
| `PRD-DIS-002` | Plain-language problem intake with PII scrubbing | Section 2 | `BD-014` |
| `PRD-DIS-003` | Adaptive structured questionnaire via HTMX/Alpine | Section 3 | `BD-015` |
| `PRD-DIS-004` | Pydantic v2 context normalization on FastAPI | Section 4 | `BD-015` |
| `PRD-DIS-005` | Ungated Executive Opportunity Map display | Section 5 | `BD-005` |
| `PRD-DIS-006` | Value-gated Technical Solution Blueprint unlock | Section 6 | `BD-005` |
| `PRD-DIS-007` | Confidence-banded indicative estimate display | Section 7 | `BD-006` |
| `PRD-DIS-008` | Mandatory non-binding legal disclaimer notice | Section 7 | `BD-006` |
| `PRD-DIS-009` | Principal Architect human review handoff trigger | Section 7 | `BD-010`, `BD-013` |
