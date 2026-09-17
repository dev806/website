# MVP Scope Definition & Feature Boundary Matrix

**Document ID:** `DOC-PRD-008`  
**Classification:** Product Definition / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-008](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-008), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Product Strategy](file:///d:/Project_website/docs/03-product/02-PRODUCT-STRATEGY.md) | [AI Discovery Spec](file:///d:/Project_website/docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Canonical Scope Boundary Baseline

---

## 1. Executive Summary & MVP Objective

The primary objective of the **Minimum Viable Product (MVP)** is to deliver an ultra-fast, premium, and functional digital presence that validates our core value proposition:

> **"We turn business problems into technology."**  
> *(Traceability: `BD-011`)*

To prevent the classic failure mode of overengineered software projects, the MVP scope is strictly defined around a single, unbroken commercial loop:
$$\text{Visitor Arrives} \longrightarrow \text{Engages AI Discovery} \longrightarrow \text{Views Opportunity Map} \longrightarrow \text{Unlocks Blueprint} \longrightarrow \text{Human Architect Reviews Dossier} \longrightarrow \text{Commercial Proposal Issued}$$

Everything that directly enables this loop is **IN SCOPE**. Everything that introduces speculative complexity, additional paid subscriptions, or maintenance overhead without proving product-market fit is **DEFERRED** or **REJECTED**.

---

## 2. Core Mandatory MVP Scope (Inclusions)

The MVP delivery must implement the following eight core capabilities:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            CORE MANDATORY MVP CAPABILITIES                       │
├─────────────────────────┬────────────────────────────────────────────────────────┤
│ 1. Studio Marketing Site│ High-performance, server-rendered landing page, service│
│                         │ catalog, philosophy, and trust architecture.           │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. AI Discovery Stepper │ 5-step guided interactive intake ("Start With Your     │
│                         │ Problem") powered by HTMX + Alpine.js (`BD-012`).      │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. Structured Ingestion │ Pydantic v2 schemas validating problems and mapping    │
│                         │ inputs into our 11 business outcome categories.        │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. Opportunity Map      │ Instant ungated real-time diagnosis separating root    │
│                         │ causes, automation tags, and complexity ratings.       │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 5. Solution Blueprint   │ Comprehensive 18-section architectural specification   │
│                         │ unlocked via corporate work email (`BD-005`).          │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 6. Indicative Estimation│ Algorithmic budget & timeline ranges with mandatory    │
│                         │ non-binding legal disclaimers (`BD-006`).              │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 7. Architect Handoff    │ Automated lead dossier dispatch notifying senior human │
│                         │ architects for proposal preparation (`BD-010`).        │
├─────────────────────────┼────────────────────────────────────────────────────────┤
│ 8. Basic Telemetry      │ Privacy-first server-side event logging tracking       │
│                         │ discovery step completions and drop-off rates.         │
└─────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Feature Evaluation Matrix

Every candidate feature has been evaluated against engineering cost, commercial necessity, and operational ROI. Features are strictly classified as **MVP**, **PHASE 2**, **FUTURE**, or **NOT JUSTIFIED**:

| Candidate Feature | Classification | Technical & Commercial Reasoning | Traceability |
| :--- | :--- | :--- | :--- |
| **Marketing Website & Service Catalog** | **`MVP`** | Fundamental commercial baseline; establishes category authority and credibility. | `BD-009`, `BD-015` |
| **Interactive AI Discovery Engine** | **`MVP`** | Signature interactive conversion asset; transforms static brochure into dynamic product. | `BD-012`, `BD-015` |
| **Progressive Lead Gating (Email)** | **`MVP`** | Balances value-first trial with commercial pipeline lead qualification (`BD-005`). | `BD-005` |
| **Indicative Estimation Algorithm** | **`MVP`** | Qualifies budget intent and filters non-serious tire-kickers transparently (`BD-006`). | `BD-006` |
| **Internal Architect Lead Dossier** | **`MVP`** | Essential human-in-the-loop operational bridge for proposal authoring (`BD-010`). | `BD-010`, `BD-013` |
| **Downloadable PDF Blueprint Export** | **`PHASE 2`** | High client value, but HTML on-screen view satisfies MVP; defer headless browser overhead. | `DEC-005` |
| **Anonymous Session Resumption** | **`PHASE 2`** | Useful for returning visitors via signed cookies/magic links; not critical for Day 1 launch. | `DEC-014` |
| **Interactive Budget Sliders** | **`PHASE 2`** | Engaging visual UI enhancement; deferred until basic linear stepper is empirically verified. | `BD-006` |
| **Self-Service Client Portal** | **`FUTURE`** | Complex auth, project management, and sprint tracking; client communication handled via email/Slack initially. | `BD-008` |
| **Internal Admin Review Portal** | **`PHASE 2`** | In MVP, architects review lead dossiers via email/webhook alerts and SSMS; custom UI not Day 1 blocker. | `BD-015` |
| **User Authentication / Passwords** | **`NOT JUSTIFIED`**| Forcing password accounts kills top-of-funnel conversion. Value-first progressive reveal requires no auth. | `BD-005` |
| **Self-Service Online Checkout** | **`NOT JUSTIFIED`**| Discovery Sprints & Builds require human architectural review and custom SOWs (`BD-006`); no self-checkout. | `BD-004`, `BD-006` |
| **Headless CMS Platform** | **`NOT JUSTIFIED`**| Adds unnecessary database and API overhead; marketing content easily managed via Jinja2 templates. | `BD-015` |
| **External Vector Database (Pinecone)**| **`NOT JUSTIFIED`**| Massive overkill for 30–50 initial solution templates; in-memory Python dictionaries operate faster at ₹0 cost. | `DEC-012` |
| **Autonomous Multi-Agent Frameworks** | **`NOT JUSTIFIED`**| LangChain/CrewAI introduce high latency, fragile dependencies, and unpredictable hallucinations. Simple pipelines prevail. | `DEC-011` |
| **Automated Contract/Proposal Generator**| **`FUTURE`** | Proposals carry legal and commercial liability; strictly reserved for human architects in early phases (`BD-010`). | `BD-010` |
| **Multi-Tenant Enterprise Discovery SaaS**| **`FUTURE`** | Commercial productization horizon (Months 18–36) once the studio intake engine is thoroughly battle-tested (`BD-008`). | `BD-008` |

---

## 4. Technical Stack Conformance (`BD-015`)

The MVP is engineered strictly within the approved, cost-effective Python-first development constraint:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             MVP DEVELOPMENT STACK                                │
├──────────────────────────┬───────────────────────────────────────────────────────┤
│ Backend Framework        │ Python 3.12+ with FastAPI (Modular Monolith)          │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Development App Server   │ Uvicorn local runner with hot reload (`--reload`)     │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Development Database     │ Microsoft SQL Server (Developer Edition) + SSMS       │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ ORM & Migrations         │ SQLAlchemy 2.x (`aioodbc` async) + Alembic            │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Frontend Architecture    │ Jinja2 Server-Side Templates + HTMX + Alpine.js       │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ AI Synthesis Interface   │ LiteLLM / Provider SDKs + Pydantic v2 Schemas         │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Development Infra Cost   │ ₹0 Infrastructure Cost (Runs entirely locally)       │
├──────────────────────────┼───────────────────────────────────────────────────────┤
│ Production Infrastructure│ Open / Decoupled (Evaluated prior to deployment)      │
└──────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 5. Definition of Done (DoD) for MVP

The MVP will be certified as complete and ready for public launch only when:

1. **Intake Continuity**: A visitor can navigate through all 5 steps of the AI Discovery Stepper and receive an Opportunity Map without server errors.
2. **Schema Integrity**: 100% of LLM outputs parse strictly into typed Pydantic v2 schemas with automated fallback handling.
3. **Lead Gating**: Entering an email successfully unlocks the full Technical Solution Blueprint and indicative budget/timeline bands.
4. **Human Handoff**: Submitting a request for human review immediately compiles and dispatches a complete lead dossier to the studio internal team.
5. **Non-Binding Notices**: Every estimate and blueprint displays the mandatory legal disclaimer (`BD-006`).
6. **Zero Paid Overhead**: The entire development environment runs locally at **₹0 infrastructure cost** on Microsoft SQL Server + SSMS (`BD-015`).

---

## 6. Traceability Matrix

| Requirement ID | MVP Scope Dimension | Section Reference | Decision Reference |
| :--- | :--- | :--- | :--- |
| `PRD-MVP-001` | Eight core mandatory MVP inclusions | Section 2 | `BD-005`, `BD-012` |
| `PRD-MVP-002` | Feature evaluation matrix & strict boundary classification | Section 3 | `BD-004`, `BD-008` |
| `PRD-MVP-003` | Rejection of unnecessary paid SaaS (Auth, Vector DB, CMS) | Section 3 | `DEC-011`, `DEC-012` |
| `PRD-MVP-004` | Python-first development stack conformance | Section 4 | `BD-015` |
| `PRD-MVP-005` | ₹0 local development infrastructure baseline | Section 4 | `BD-015` |
| `PRD-MVP-006` | Six-point operational Definition of Done (DoD) | Section 5 | `BD-006`, `BD-010` |
