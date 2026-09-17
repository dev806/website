# Executive Opportunity Map: Technical Specification

**Document ID:** `DOC-PRD-004`  
**Classification:** Product Specification / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010)  
**Parent Framework:** [AI Discovery Spec](file:///d:/Project_website/docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md) | [Customer Problems](file:///d:/Project_website/docs/01-business/CUSTOMER_PROBLEMS.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Canonical Product Specification

---

## 1. Executive Summary & Purpose

The **Executive Opportunity Map** is the immediate, real-time diagnostic deliverable generated at Stage 4 of the AI Discovery process.

Its core purpose is **analytical synthesis**: transforming a messy, colloquial problem description into a structured, prioritized matrix of technological interventions. It proves to the prospective client that `[STUDIO_NAME]` grasps their commercial bottlenecks, separates root causes from surface symptoms, and understands where software and automation will create genuine financial return.

It is presented **100% ungated** to fulfill our value-first lead generation strategy (`BD-005`).

---

## 2. Input Parameter Pipeline

The Opportunity Map engine ingests structured and unstructured data points captured during Stages 1 and 2:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            OPPORTUNITY MAP INGESTION PIPELINE                    │
├───────────────────────┬──────────────────────────────────────────────────────────┤
│ Input Parameter       │ Source & Description                                     │
├───────────────────────┼──────────────────────────────────────────────────────────┤
│ Raw Problem Statement │ Unstructured text prompt explaining the business friction│
├───────────────────────┼──────────────────────────────────────────────────────────┤
│ Industry Sector       │ Domain classification (Healthcare, Logistics, Fintech...)│
├───────────────────────┼──────────────────────────────────────────────────────────┤
│ Organizational Scale  │ Team size & volume tier (Solo, 2–10, 11–50, 51–200, 200+)│
├───────────────────────┼──────────────────────────────────────────────────────────┤
│ Technical Maturity    │ Level 1 (Manual) to Level 4 (Modern/Scaling)             │
├───────────────────────┼──────────────────────────────────────────────────────────┤
│ Primary Friction Area │ Data Entry / Fragmented Tools / Speed / Cost / Dev Bandw.│
├───────────────────────┼──────────────────────────────────────────────────────────┤
│ Urgency & Horizon     │ < 1 Month (Urgent) / 1–3 Months / Strategic Horizon      │
└───────────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 3. Output Schema & Component Display

The Opportunity Map renders a structured dashboard consisting of five distinct information modules:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      EXECUTIVE OPPORTUNITY MAP DISPLAY LAYOUT                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. THE ROOT CAUSE DIAGNOSIS                                                      │
│    "Your order delays are not caused by staff speed, but by manual double data   │
│     entry between WhatsApp customer inquiries and an isolated Tally ledger."     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 2. CATEGORIZED OPPORTUNITY TAGS                                                  │
│    [AUTOMATION: High Priority]  [INTEGRATION: Medium Priority]  [AI: Near-Term] │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 3. THE INTERVENTION MATRIX                                                       │
│    • Quick Win: Automated WhatsApp order confirmation webhook                    │
│    • Core Build: Centralized FastAPI order management portal                     │
│    • Scalability: Scheduled daily financial sync to accounting                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 4. TECHNICAL UNKNOWNS & ARCHITECTURAL RISKS                                      │
│    • Unknown: API version and webhook capabilities of current ERP/legacy system  │
│    • Risk: WhatsApp message volume limits without Meta business verification     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 5. COMPLEXITY & EFFORT SIGNALS                                                   │
│    Architectural Effort: MODERATE  |  Integration Surface: 3 External APIs       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Five Opportunity Categories

The diagnostic engine maps every identified opportunity into one of five structured technology categories:

1. **Workflow Automation Opportunities (`OPP-AUT`)**:
   - Eliminating repetitive manual copy-pasting, spreadsheet updates, and notification emails.
   - *Example*: Event-driven order dispatch, automatic PDF receipt generation, invoice parsing.
2. **AI Capability Opportunities (`OPP-AI`)**:
   - Embedding cognitive intelligence into data extraction, classification, or conversational intake.
   - *Example*: Intelligent Document Processing (IDP), RAG internal knowledge retrieval, triage agents.
3. **Core Application Build Opportunities (`OPP-BLD`)**:
   - Engineering bespoke web applications, customer self-service portals, or relational databases.
   - *Example*: Role-based operations portal, client booking dashboard, modular MVP web app.
4. **System Integration Opportunities (`OPP-INT`)**:
   - Connecting disparate third-party platforms, CRMs, payment rails, and legacy databases into a unified real-time pipeline.
   - *Example*: Razorpay/Stripe webhooks, Zoho/HubSpot synchronization, logistics API adapters.
5. **Infrastructure & Scale Opportunities (`OPP-SCL`)**:
   - Stabilizing deployment topology, optimizing slow database queries, and locking in predictable hosting.
   - *Example*: Docker containerization, Caddy auto-HTTPS proxying, snapshot backup automation.

---

## 5. Prioritization Framework (Proposed Design Candidates)

To prevent cognitive overload, the engine evaluates and ranks identified interventions across four key dimensions:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      PROPOSED PRIORITIZATION EVALUATION CRITERIA                 │
├─────────────────────┬────────────────────────────────────────────────────────────┤
│ Evaluation Vector   │ Proposed Assessment Logic (Candidate Heuristics)           │
├─────────────────────┼────────────────────────────────────────────────────────────┤
│ 1. Business Impact  │ High: Directly increases revenue, margin, or saves >15 hrs/│
│                     │       week of skilled labor.                               │
│                     │ Medium: Improves data quality, customer response speed.    │
│                     │ Low: Minor aesthetic or non-critical convenience feature.  │
├─────────────────────┼────────────────────────────────────────────────────────────┤
│ 2. Technical        │ Low: Standard CRUD, existing reusable components, zero APIs│
│    Complexity       │ Med: Multi-system webhooks, relational schema state machine│
│                     │ High: Legacy data migration, custom ML model fine-tuning.  │
├─────────────────────┼────────────────────────────────────────────────────────────┤
│ 3. Implementation   │ Immediate (< 2 weeks): Pre-built reusable automation module│
│    Feasibility      │ Standard (3–6 weeks): Modular monolith build + 2 APIs.     │
│                     │ Extended (> 6 weeks): Complex distributed integrations.    │
├─────────────────────┼────────────────────────────────────────────────────────────┤
│ 4. Operational      │ Critical: Current process actively causing lost revenue.   │
│    Urgency          │ Moderate: Inefficiency tolerated but limits growth.        │
│                     │ Horizon: Future capability desirable when scale doubles.   │
└─────────────────────┴────────────────────────────────────────────────────────────┘
```

* **Important Note on Scoring Governance**: The heuristics above are **proposed design candidates** used internally by the prompt synthesis engine. The system does not output false mathematical precision (e.g. *"Priority Score: 8.74/10"*); it outputs clear qualitative bands: **"Immediate Quick Win"**, **"Core Structural Build"**, and **"Phase 2 Scale Opportunity"**.

---

## 6. Identifying Risks, Dependencies & Technical Unknowns

A core differentiator of `[STUDIO_NAME]` is **radical candor**. Where other agencies make optimistic promises, the Opportunity Map deliberately surfaces uncertainties:

* **Technical Dependencies (`DEP-*`)**: Identifies external blockers before coding begins (e.g. *"Requires official Meta WhatsApp Cloud API credentials"*, *"Requires access to legacy SQL database schema"*).
* **Architectural Risks (`RSK-*`)**: Highlights commercial or operational pitfalls (e.g. *"API rate limits on third-party accounting software may require asynchronous queueing"*).
* **Unknowns Requiring Human Review (`UNK-*`)**: Explicitly enumerates questions that the AI engine cannot answer autonomously (e.g. *"Need to inspect historical data cleaning requirements before migrating to relational database"*).

---

## 7. The Human Architect Review Points (`BD-010`)

The Opportunity Map is explicitly designed as a collaborative artifact between the prospective client and our human systems architects:

```text
PROSPECTIVE CLIENT                                     STUDIO PRINCIPAL ARCHITECT
──────────────────                                     ──────────────────────────
• Views initial automated map on web.            ──►   • Inspects raw intake prompt & domain context.
• Unlocks full blueprint via work email.         ──►   • Validates whether root cause diagnosis is accurate.
• Clicks "Request Principal Architect Review".   ──►   • Calibrates complexity ranking and removes edge risks.
                                                 ──►   • Prepares tailored Statement of Work (SOW).
```

* **Gatekeeping Rule**: If the AI engine misclassifies a complex problem (e.g. suggesting an off-the-shelf integration when an uncooperative legacy database requires custom drivers), the human Principal Architect intervenes during proposal preparation to correct the architecture before any commercial agreement is signed.

---

## 8. Traceability Matrix

| Requirement ID | Opportunity Map Dimension | Section Reference | Decision Reference |
| :--- | :--- | :--- | :--- |
| `PRD-MAP-001` | Instant ungated delivery at Stage 4 of discovery | Section 1 | `BD-005` |
| `PRD-MAP-002` | Six-point input parameter ingestion pipeline | Section 2 | `BD-011`, `BD-012` |
| `PRD-MAP-003` | Five structured opportunity categorization classes | Section 4 | `BD-009`, `BD-015` |
| `PRD-MAP-004` | Qualitative 4-vector prioritization heuristics | Section 5 | `BD-006` |
| `PRD-MAP-005` | Explicit surfacing of dependencies, risks & unknowns | Section 6 | `BD-006`, `BD-010` |
| `PRD-MAP-006` | Principal Architect human review checkpoints | Section 7 | `BD-010`, `BD-013` |
