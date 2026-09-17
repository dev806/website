# PROJECT ASSUMPTIONS REGISTER
**Systematic Inventory of Hypotheses, Baseline Assumptions, and Validation Protocols**

---
Document Owner: Principal Project Architect & Systems Planner  
Status: PROPOSED  
Version: 1.0.0  
Last Updated: 2026-09-07  
Dependencies: [PROJECT_OVERVIEW.md](file:///d:/Project_website/docs/00-project/PROJECT_OVERVIEW.md)  
Related Documents: [DECISION_LOG.md](file:///d:/Project_website/docs/00-project/DECISION_LOG.md), [REQUIREMENTS_REGISTER.md](file:///d:/Project_website/docs/00-project/REQUIREMENTS_REGISTER.md)  
Decision Status: UNDER_REVIEW  
---

## 1. Purpose & Governance

Every project relies on foundational assumptions across market dynamics, user behavior, technical feasibility, and unit economics. Treating unverified assumptions as established facts leads to premature optimization, misallocated engineering resources, and commercial failure.

This register catalogs every active assumption, assigns an explicit confidence score, assesses the blast radius if invalidated, and defines the empirical validation method required before committing capital or irreversible engineering time.

---

## 2. Assumptions Register Matrix

| ID | Category | Assumption Statement | Rationale / Why It Exists | Confidence | Impact if Wrong | Validation Method | Owner | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ASM-BUS-001`** | Business | B2B decision-makers will engage with an interactive AI discovery tool rather than booking a direct sales call immediately. | Modern buyers prefer self-service discovery and immediate diagnostic feedback over high-pressure sales calls. | Medium (50%) | High | A/B test website landing page: AI Discovery CTA vs Direct "Book a Call" Calendly form. Track completion and qualification rates. | Growth / Product | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-BUS-002`** | Business | Qualified enterprise prospects will purchase a Paid Discovery Sprint when credited toward the build contract (pricing, duration, packaging, and crediting TBD). | Enterprise buyers value de-risking architecture; credit toward build fee removes downside. | Medium (50%) | Critical | Pilot with inbound leads. Measure close rate; test duration, packaging, and crediting terms. | Commercial Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-BUS-003`** | Business | Indian market pricing can sustain healthy gross margins while remaining attractive to domestic SMEs. | Domestic SMEs require localized INR pricing with GST credits, whereas global clients benchmark in USD. | Medium (60%) | High | Price sensitivity interviews with target SME founders in India. | Commercial Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-BUS-004`** | Business | A meaningful portion of recurring patterns, components, integrations, workflows, and architectural knowledge can become reusable across projects. | Standardization of common plumbing accelerates delivery and expands margins without starting from scratch. | Medium (55%) | High | Track component extraction and engineering hours across initial project deliveries. | Technical Architect | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-BUS-005`** | Business | 100% client code ownership (zero vendor lock-in) is an attractive differentiator against traditional agency lock-in models. | Clients want to own their proprietary technology assets upon paying milestone fees. | Medium (60%) | Medium | Test resonance of IP ownership proposition during sales conversations. | Product Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-USR-001`** | User | Non-technical business owners can clearly articulate business problems without needing to know technical solutions. | Core premise: "We turn business problems into technology." | High (70%) | Critical | Conduct user testing sessions with non-technical SME owners using problem prompts. | UX Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-USR-002`** | User | Users prefer guided multi-choice selectors paired with contextual text over a blank open chatbot prompt. | Open chat boxes suffer from "blank page syndrome" and high mobile typing drop-off. | High (75%) | High | Measure drop-off rates across multi-step guided prototype vs conversational sandbox. | UX Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-USR-003`** | User | Users will provide corporate email to unlock the detailed Solution Blueprint after viewing an initial high-level Opportunity Map. | Progressive profiling delivers initial value before gating deeper technical IP. | Medium (60%) | Critical | Track gate conversion rate in discovery prototype funnel. | Product Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-TEC-001`** | Technical | FastAPI + Jinja2 + HTMX + Alpine.js provides sufficient SSR performance and reactive streaming capabilities for discovery interactions at ₹0 dev cost. | Aligns with Project Owner's Python expertise and eliminates Node.js build tooling. | High (85%) | High | Benchmark prototype response times and streaming token latency locally. | Tech Lead | `CONFIRMED DEV CONSTRAINT (BD-015)` |
| **`ASM-TEC-002`** | Technical | Microsoft SQL Server (dev) via SQLAlchemy provides robust local relational persistence and debugging with SSMS at ₹0 cost. | Developer familiarity and maintainability; production DB decoupled. | High (90%) | High | Verify Alembic migrations and async connection pooling with local SQL Server instance. | Data Architect | `CONFIRMED DEV CONSTRAINT (BD-015)` |
| **`ASM-TEC-003`** | Technical | Lean flat-rate or low-cost hosting (e.g. Linux VPS via Docker Compose) can handle launch traffic with sub-second page loads. | Studio must maintain predictable, low infrastructure burn rate. | Medium (65%) | Medium | Execute load test simulating 50 concurrent discovery sessions. | DevOps Lead | `HYPOTHESIS — TO BE EVALUATED LATER` |
| **`ASM-AI-001`** | AI | LLMs via LiteLLM / direct SDKs can reliably extract structured problem parameters into typed Pydantic v2 schemas. | Discovery engine relies on deterministic downstream UI components parsing AI outputs. | High (80%) | High | Benchmark business problem prompts through OpenAI, Anthropic, and Gemini structured outputs. | AI Architect | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-AI-002`** | AI | Cost-efficient frontier or small models (e.g. Gemini Flash, Claude Haiku, GPT-4o-mini) are sufficient for problem classification. | Minimizes inference cost per discovery session. | Medium (65%) | Medium | Run comparative benchmark across providers on classification accuracy and latency. | AI Architect | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-AI-003`** | AI | Algorithmic timeline and cost estimation based on complexity heuristics provides indicative ranges to qualify intent without generating binding quotes. | Pricing transparency qualifies budget without legal quotation exposure (`BD-006`). | Medium (50%) | Critical | Backtest estimation algorithm against real-world software project scopes. | Solutions Architect | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-MKT-001`** | Market | Inbound organic SEO and technical problem-first thought leadership can generate qualified B2B leads without heavy paid ad spend initially. | Problem-first case studies and technical articles target high-intent search queries. | Medium (55%) | High | Track organic impressions, click-through rates, and lead attribution during first 90 days. | Marketing Lead | `HYPOTHESIS — VALIDATION REQUIRED` |
| **`ASM-MKT-002`** | Market | Indian growth businesses in Tier 1/2 hubs are actively prioritizing process modernization and AI workflows. | High regional digital transformation and appetite for operational automation. | Medium (50%) | High | Validate through inbound lead regional demographics and primary customer discovery interviews. | Commercial Lead | `MARKET HYPOTHESIS — RESEARCH REQUIRED` |
| **`ASM-OPS-001`** | Operations | A human Principal Architect can review and calibrate an AI-generated proposal within 24 business hours as an internal target. | Fast turnaround creates high consultative trust without contractual SLA penalties (`BD-013`). | Medium (60%) | Medium | Measure architect review duration per proposal draft during initial operations. | Operations Lead | `HYPOTHESIS — INTERNAL TARGET ONLY` |
| **`ASM-SEC-001`** | Security | Zero-data-retention agreements and prompt PII sanitization are sufficient to satisfy enterprise client privacy concerns during discovery. | Prospective clients will not input proprietary secrets without strong data hygiene guarantees (`BD-014`). | High (75%) | Critical | Review privacy policy and sanitization pipeline against best-practice standards. | Security Architect | `HYPOTHESIS — VALIDATION REQUIRED` |

---

## 3. Assumption Lifecycle Management

1. **PROPOSED**: Identified hypothesis pending validation plan.
2. **VALIDATING**: Active experiment or user study underway.
3. **VALIDATED**: Empirical data confirms hypothesis; assumption transitions to a confirmed requirement.
4. **INVALIDATED**: Empirical data disproves hypothesis; associated architectural decision is updated via `DECISION_LOG.md`.
