# PROJECT CONSTRAINTS REGISTER
**Registry of Confirmed Operational Boundaries, Proposed Policies, and Open Constraints**

---
Document Owner: Principal Project Architect & Systems Planner  
Status: PROPOSED  
Version: 1.0.0  
Last Updated: 2026-09-07  
Dependencies: [PROJECT_OVERVIEW.md](file:///d:/Project_website/docs/00-project/PROJECT_OVERVIEW.md)  
Related Documents: [DECISION_LOG.md](file:///d:/Project_website/docs/00-project/DECISION_LOG.md), [TECHNOLOGY_DECISION_FRAMEWORK.md](file:///d:/Project_website/docs/00-project/TECHNOLOGY_DECISION_FRAMEWORK.md)  
Decision Status: UNDER_REVIEW  
---

## 1. Classification Methodology

To ensure architectural integrity, constraints are strictly categorized into three distinct levels of certainty:
1. **CONFIRMED CONSTRAINTS**: Explicitly mandated by project leadership or non-negotiable legal/business requirements.
2. **PROPOSED CONSTRAINTS**: Pragmatic engineering, operational, or budgetary recommendations awaiting executive sign-off.
3. **UNKNOWN / DECISION REQUIRED**: Critical operational boundaries that are currently undefined and require leadership resolution.

---

## 2. Confirmed Constraints

* **`CST-CNF-001` (Pre-Development Gate)**: No production application code, frontend scaffolding, backend database initialization, or cloud resource provisioning may begin until the documentation architecture audit is complete and critical decisions are formally signed off. (Source: Master Prompt Section 1 & 20)
* **`CST-CNF-002` (Mandatory Human Gate)**: AI systems are strictly prohibited from generating legally binding commercial contracts, statements of work, or final pricing commitments without explicit inspection and sign-off by a licensed studio Principal Architect. (Source: Master Prompt Section 3)
* **`CST-CNF-003` (Target Market Boundary)**: The initial launch market is Startups, SMEs, and Growing Businesses, structured for immediate deployment in India with architectural readiness for global expansion. (Source: Master Prompt Section 1)
* **`CST-CNF-004` (Core Positioning Mandate)**: The platform and public website must position the company as a "Premium Technology Partner" operating under the philosophy: *"Technology should adapt to the business — not the business to technology."* (Source: Master Prompt Section 1)
* **`CST-CNF-005` (Capability Scope Boundary)**: The studio's service offerings must map to the 5 designated capability pillars: **BUILD**, **AI**, **AUTOMATE**, **INTEGRATE**, and **SCALE**. (Source: Master Prompt Section 1)
* **`CST-CNF-006` (Documentation Structure)**: Documentation must reside in `/docs` partitioned into logical domain folders (`00-project` through `20-roadmap`) maintaining traceability from business requirements to automated tests. (Source: Master Prompt Section 6 & 10)
* **`CST-CNF-007` (Python-First Engineering Constraint)**: The entire core platform must be built within the Python ecosystem (Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, Jinja2/HTMX/Alpine) to ensure the Project Owner can understand, maintain, debug, and extend the system independently. (Source: Hard Constraint Directive)
* **`CST-CNF-008` (Development Database & Server Constraint)**:
  - **Development Database**: Microsoft SQL Server + SQL Server Management Studio (SSMS) accessed via SQLAlchemy 2.x (`aioodbc` async driver / `pyodbc` sync driver) and Alembic migrations.
    - **Rationale**: The Project Owner possesses established practical expertise with SQL Server and SSMS. Prioritizes developer familiarity, rapid iteration, and maintainability while keeping development as simple and manageable as possible.
    - **Elimination of Unnecessary Complexity**: Do NOT introduce PostgreSQL for development, SQLite merely for testing, Redis, MongoDB, vector databases, or multiple databases during the development phase. The MVP development environment has exactly **ONE primary development database: Microsoft SQL Server**.
    - **Testing Strategy**: Tests execute against a dedicated local SQL Server test database (`StudioWebsiteTest`) using transactional rollbacks, eliminating dialect discrepancies. Do NOT assume SQLite is required for development or testing.
  - **Development Server**: Local machine running the FastAPI ASGI development server via **Uvicorn with hot reload** (`uvicorn main:app --reload`), connecting locally to Microsoft SQL Server at **₹0 infrastructure/hosting cost**. No paid cloud server or external hosting is permitted or required for the initial development phase.
  - **Production Independence**: Production architecture must remain a completely separate decision and must NOT be locked based on this development requirement. Production database engine and cloud hosting environment will be evaluated separately later.
  - **Optimization Divergence**:
    - *Development Environment Optimizes For*: (1) Project-owner familiarity, (2) Zero infrastructure cost (₹0), (3) Easy local setup, (4) Fast iteration, (5) Maintainability, (6) Compatibility with the planned architecture.
    - *Production Environment Will Later Optimize For*: (1) Reliability, (2) Security, (3) Backup/recovery, (4) Performance, (5) Scalability, (6) Cost efficiency. (Source: Hard Constraint Directive)

---

## 3. Proposed Constraints (Awaiting Confirmation)

* **`CST-PRP-001` (Cost-Linear / Free-Tier Infrastructure Budget)**: During pre-launch and MVP Phase 1, total monthly cloud infrastructure and third-party SaaS operating costs should target a ceiling of $< \$100/\text{month}$, leveraging free tiers and open-source software where technically viable.
* **`CST-PRP-002` (Architectural Simplicity / Monolithic Baseline)**: The MVP platform should be implemented as a modular full-stack application (or modular monolith) rather than a distributed microservices network to minimize operational complexity, deployment friction, and latency.
* **`CST-PRP-003` (Proposal Turnaround Policy)**: Propose a target operating turnaround of 24 business hours for human Principal Architect review of qualified proposal requests. *(Note: Must be validated against team capacity before publishing as a customer SLA).*
* **`CST-PRP-004` (Browser & Device Support Baseline)**: Support modern evergreen desktop and mobile browsers (Chromium >= 120, Safari >= 17, Firefox >= 120, iOS Safari >= 17) with responsive layouts tested from 360px width to 4K displays.
* **`CST-PRP-005` (Dual-Currency Accounting Protocol)**: Invoicing and payment processing should support INR (`₹`) via domestic rails (UPI/NEFT/Cards with GST invoicing) and USD (`$`) for international engagements.

---

## 4. Unknown / Decision Required Constraints

* **`CST-UNK-001` (Official Legal & Brand Identity)**: Legal corporate name, trademark status, and official primary web domain are unconfirmed (`DEC-001`).
* **`CST-UNK-002` (Hard Project Launch Deadline)**: Target public launch date for MVP has not been established (e.g., 6 weeks, 12 weeks, or milestone-driven).
* **`CST-UNK-003` (Data Sovereignty Mandate)**: Whether client discovery data must reside exclusively on servers physically located within India (per domestic data protection guidelines) or if global cloud regions (e.g., AWS us-east-1, Vercel global edge) are acceptable.
* **`CST-UNK-004` (Dedicated Engineering Team Size)**: The exact number of engineers and designers available for the Phase 1 build has not been declared, impacting sprint velocity assumptions.
* **`CST-UNK-005` (Third-Party Model Vendor Restrictions)**: Whether prospective enterprise clients possess contractual restrictions forbidding data transit through specific commercial AI API providers (OpenAI, Anthropic, Google).
