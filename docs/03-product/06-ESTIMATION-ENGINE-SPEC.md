# Estimation Engine: Conceptual Architecture & Specification

**Document ID:** `DOC-PRD-006`  
**Classification:** Product Specification / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-007](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-007), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-013](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-013), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [AI Discovery Spec](file:///d:/Project_website/docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md) | [Business Model](file:///d:/Project_website/docs/01-business/BUSINESS_MODEL.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Conceptual Estimation Specification (No Fixed Prices Hard-Coded)

---

## 1. Executive Summary & Purpose

The **Estimation Engine** is the algorithmic sizing and planning subsystem of the AI Discovery platform.

Its objective is to **qualify commercial intent and align budget expectations** by calculating **confidence-banded indicative planning ranges** (timeline and budget) based on empirical complexity signals.

In strict compliance with owner decisions (`BD-006`, `BD-010`):
* **Zero False Precision**: The engine never outputs a single deceptive number (e.g. *"This project will cost exactly ₹2,47,500"*). It calculates bounded low-to-high ranges.
* **Zero Autonomous Quotations**: The output is explicitly labeled as a non-binding planning estimate. Legally binding proposals and fixed Statements of Work (SOW) strictly require human Principal Architect review.
* **Zero Hard-Coded Price Anchors**: The formula is parameterized; no unauthorized fixed price tables are hard-coded in this document (`BD-007`).

---

## 2. Input Parameter Pipeline (Complexity Signals)

The estimation model evaluates eight distinct architectural vectors captured during diagnostic intake:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            ESTIMATION INPUT SIGNAL MATRIX                        │
├─────────────────────────┬────────────────────────────────────────────────────────┤
│ Input Signal Vector     │ Complexity Spectrum & Impact Factors                   │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Scope Archetype      │ MVP Prototype / Custom Web App / Internal Operations   │
│                         │ Portal / Multi-Tenant SaaS Foundation.                 │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. Functional Scale     │ Number of distinct user roles (1–4) & core CRUD views. │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. External Integrations│ None / 1–2 Standard APIs (Stripe, WhatsApp) /          │
│                         │ 3+ Complex Enterprise APIs (Legacy ERPs, Custom Banks).│
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. AI Complexity        │ None / Direct Prompt Pipeline / RAG Document Search /  │
│                         │ Autonomous State-Machine Agents.                       │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 5. Workflow Automation  │ None / Simple Webhook Alerts / Multi-Step Orchestration│
│                         │ with Failure Retry Queues.                             │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 6. Data Migration Scale │ Green-field (Zero data) / Structured CSV import /      │
│                         │ Messy legacy database extraction & sanitization.       │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 7. Security & Compliance│ Standard OWASP / Multi-Tenant RBAC / Compliance-Ready  │
│                         │ PII Encryption & Audit Logging (`BD-014`).             │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 8. Uncertainty Factor   │ Low (Standard patterns) / High (Unverified 3rd-party   │
│    (Unknowns & Risks)   │ legacy APIs, undefined commercial logic).              │
└─────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Conceptual Estimation Algorithm (Python-First Heuristic Model)

The estimation algorithm is implemented as a deterministic Python formula executed on the FastAPI backend (`BD-015`).

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         CONCEPTUAL SIZING FORMULA FLOW                           │
│                                                                                  │
│   [Base Archetype Effort Units]                                                  │
│                +                                                                 │
│   ∑ [Feature Complexity Units (Roles, Views, State Machine)]                     │
│                +                                                                 │
│   ∑ [Integration Multipliers (APIs, Webhooks, Auth)]                             │
│                +                                                                 │
│   ∑ [AI Pipeline Surcharge (RAG, Chunking, Vector Storage)]                      │
│                ×                                                                 │
│   [Uncertainty Multiplier (Driven by Unknowns & Data Migration)]                 │
│                ║                                                                 │
│                ▼                                                                 │
│   Total Estimated Engineering Effort Units (Effort-Hours)                        │
│                ║                                                                 │
│        ┌───────┴───────┐                                                         │
│        ▼               ▼                                                         │
│   TIMELINE BANDS   BUDGET BANDS                                                  │
│   (Calendar Weeks) (Locale Currency: INR / USD)                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Timeline Band Calculation
$$\text{Min Weeks} = \text{RoundUp}\left(\frac{\text{Effort Units} \times 0.85}{\text{Studio Sprint Velocity}}\right)$$
$$\text{Max Weeks} = \text{RoundUp}\left(\frac{\text{Effort Units} \times 1.25 \times \text{Uncertainty Factor}}{\text{Studio Sprint Velocity}}\right)$$
* *Example Output*: **4 to 7 Weeks** to production deployment.

### 3.2 Budget Band Calculation
$$\text{Low Band} = \text{Effort Units} \times \text{Base Unit Rate} \times 0.90$$
$$\text{High Band} = \text{Effort Units} \times \text{Base Unit Rate} \times 1.30 \times \text{Uncertainty Factor}$$
* *Display Policy*: Rendered dynamically in `INR (₹)` for domestic Indian visitors or `USD ($)` for international visitors based on geo-routing (`BD-003`).

---

## 4. Output Presentation & Uncertainty Display

The estimation module is displayed at Stage 6 with three explicit components:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           ESTIMATION ENGINE USER DISPLAY                         │
├──────────────────────────────────────┬───────────────────────────────────────────┤
│ INDICATIVE INVESTMENT RANGE          │ INDICATIVE TIMELINE                       │
│ Low Band  ──────►  High Band         │ 4 Weeks  ──────►  7 Weeks                 │
│ (e.g. ₹X,XX,000 to ₹Y,YY,000 / $A–$B)│ (Calendar weeks to production launch)     │
├──────────────────────────────────────┴───────────────────────────────────────────┤
│ ESTIMATION CONFIDENCE METER: [ MEDIUM CONFIDENCE ]                               │
│ • Range Driver: Uncertainty regarding legacy ERP API documentation and webhook   │
│   stability expands the upper boundary.                                          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ EXPLICIT ESTIMATION ASSUMPTIONS:                                                 │
│ • Assumes client provides clean data exports and timely DNS/SSL access.          │
│ • Assumes standard Meta WhatsApp Business API approval without policy delays.    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Mandatory Legal Disclaimers & Governance Rules (`BD-006`)

> [!IMPORTANT]
> ### Mandatory Non-Binding Estimation Disclaimer
> Every automated estimation output—on screen, in exported summaries, or in follow-up emails—must display the following non-binding notice:  
> **"IMPORTANT NOTICE: Indicative Planning Range Only. The figures and delivery timelines presented above are algorithmic planning estimates derived from technical complexity signals. They do NOT constitute a binding quotation, commercial offer, or contract. Final architecture, scope ceilings, and legally binding Statements of Work (SOW) strictly require formal review and authorization by a studio Principal Architect."**  
> *(Traceability: `BD-006`, `PRD-EST-001`)*

### Governance Rules:
1. **Never Call It a "Quote"**: Internal and external copy must use the terms *"Indicative Planning Range"*, *"Indicative Estimate"*, or *"Complexity Band"*. The word *"Quote"* is strictly prohibited for AI-generated figures.
2. **Never Conceal Underlying Assumptions**: The UI must display the core assumptions that generated the range so the client understands why the bounds exist.
3. **Never Lower Estimates to Win Sales**: We do not engage in artificial price deflation. If a project has high integration complexity, the estimation engine honestly reflects that complexity.

---

## 6. The Human Architect Calibration Gate (`BD-010`)

When the user requests a formal proposal, the algorithmic estimate serves as the starting baseline for the human architect's evaluation:

```text
ALGORITHMIC ESTIMATE                            PRINCIPAL ARCHITECT CALIBRATION
────────────────────                            ───────────────────────────────
• Analyzes prompt keywords & tags.       ──►    • Inspects client's actual workflow reality.
• Applies standard complexity formula.   ──►    • Evaluates studio reusable component inventory.
• Generates broad indicative range.      ──►    • Eliminates unneeded features to reduce cost.
                                         ──►    • Authors formal, fixed-scope Statement of Work (SOW).
```

* **Human Override**: The Principal Architect has full authority to narrow the band, identify reusable pre-built assets that reduce cost, or adjust timelines before issuing a formal proposal.

---

## 7. Traceability Matrix

| Requirement ID | Estimation Engine Dimension | Section Reference | Decision Reference |
| :--- | :--- | :--- | :--- |
| `PRD-EST-001` | Mandatory non-binding legal disclaimer notice | Section 5 | `BD-006` |
| `PRD-EST-002` | Eight-vector complexity input pipeline | Section 2 | `BD-006`, `BD-015` |
| `PRD-EST-003` | Deterministic Python calculation model | Section 3 | `BD-015` |
| `PRD-EST-004` | Confidence-banded low/high budget and timeline | Section 4 | `BD-006`, `BD-007` |
| `PRD-EST-005` | Explicit display of driving assumptions | Section 4 | `BD-006` |
| `PRD-EST-006` | Principal Architect human review calibration gate | Section 6 | `BD-010`, `BD-013` |
| `PRD-EST-007` | Dual-currency presentation support (INR/USD) | Section 3.2 | `BD-003` |
