# Architecture Decision Records (ADR Canon)

**Document ID:** `DOC-ARCH-002`  
**Classification:** System Architecture / Phase 4 Architectural Decisions  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001) through [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [Decision Log](file:///d:/Project_website/docs/00-project/DECISION_LOG.md) | [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. ADR Governance Rules & Status Taxonomy

All architectural choices for `[STUDIO_NAME]` are governed by explicit decision records. In strict compliance with project governance, no decision is marked `APPROVED` unless explicitly signed off by the Project Owner.

Permitted statuses:
- **`APPROVED BY OWNER (BD-xxx)`**: Ratified, binding business/architectural law.
- **`CONFIRMED (CST-CNF-xxx)`**: Mandatory technical constraint.
- **`RECOMMENDED`**: Evaluated best-in-class option awaiting owner review.
- **`PROPOSED`**: Candidate option under architectural consideration.
- **`TECHNICAL EVALUATION REQUIRED`**: Requires empirical benchmarking before commitment.

---

## 2. Register of Architecture Decision Records

---

### `ADR-001`: Architectural Topology — Modular Monolith vs. Distributed Microservices
* **Status**: `CONFIRMED (CST-PRP-002, BD-015)`
* **Context**: The studio requires rapid iteration, low operational overhead, unified transaction boundaries, and single-engineer maintainability during development and early production.
* **Options Evaluated**:
  1. *Distributed Microservices*: Multiple decoupled services (Auth service, Discovery service, Content service) communicating via gRPC/REST.
  2. *Modular Monolith*: A single unified Python FastAPI application with strictly isolated domain packages, clear internal interfaces, and a shared database schema.
* **Decision / Recommendation**: Adopt the **Modular Monolith**.
* **Rationale**: Microservices introduce severe distributed systems overhead (network latency, distributed transactions, multi-repo CI/CD, complex local debugging) that is completely unjustified for MVP volume. A modular monolith provides the code organization and clean boundary benefits of microservices without the operational tax.
* **Cost & Complexity**: Minimizes cloud hosting complexity to a single process; local setup runs at **₹0 cost**.
* **Reversibility**: High. Because modules have strict interfaces, any single module (e.g. `discovery`) can be extracted into an independent microservice later if traffic warrants.

---

### `ADR-002`: Frontend Architecture — Jinja2 + HTMX + Alpine.js vs. React/Next.js SPA
* **Status**: `CONFIRMED (BD-015, CST-CNF-007)`
* **Context**: Modern web design requires responsive reactivity, sub-second load times, excellent SEO crawlability, and zero build toolchain bloat, while honoring the Python-First hard constraint.
* **Options Evaluated**:
  1. *React / Next.js / TypeScript SPA*: Separate frontend application with Node.js build pipeline and client-side JSON API hydration.
  2. *Jinja2 + HTMX + Alpine.js + Vanilla CSS*: Server-side rendered HTML partials with dynamic DOM morphing (HTMX ~14KB) and micro-interactions (Alpine.js ~15KB).
* **Decision / Recommendation**: Adopt **FastAPI + Jinja2 + HTMX + Alpine.js**.
* **Rationale**: Eliminates the entire Node.js/npm build ecosystem, package vulnerabilities, and hydration lag. Provides native semantic HTML crawlability for search engines, targets fast First Contentful Paint, and allows the Project Owner to maintain the entire application in Python.
* **Cost & Complexity**: Zero frontend build pipeline; runs natively via static assets.
* **Reversibility**: Moderate. Backend REST endpoints are clean and structured; a separate React SPA could consume them in the future if an enterprise portal demands it.

---

### `ADR-003`: Backend Framework — FastAPI vs. Flask vs. Django
* **Status**: `CONFIRMED BY OWNER (BD-015, CST-CNF-007)`
* **Context**: The backend must handle asynchronous I/O (streaming LLM tokens, concurrent database queries), provide robust type validation, and offer automatic API documentation.
* **Options Evaluated**:
  1. *Django*: Full-featured batteries-included framework with built-in admin and ORM.
  2. *Flask*: Lightweight WSGI framework.
  3. *FastAPI*: Modern ASGI framework built on Starlette and Pydantic v2.
* **Decision / Recommendation**: Adopt **FastAPI (Python 3.12+)**.
* **Rationale**: FastAPI natively supports asynchronous coroutines (`async`/`await`) essential for high-latency external LLM API calls without thread exhaustion; enforces strict runtime typing via Pydantic v2; and automatically generates interactive OpenAPI/Swagger schemas.
* **Cost & Complexity**: Extremely lightweight, highly performant, open source.
* **Reversibility**: High. Business logic is separated into domain services, making framework migration straightforward.

---

### `ADR-004`: Development Database Engine — Microsoft SQL Server + SSMS
* **Status**: `CONFIRMED BY OWNER (CST-CNF-008, BD-015)`
* **Context**: The Project Owner possesses established practical expertise with Microsoft SQL Server and SSMS. Local development must prioritize maintainability, developer familiarity, and ₹0 cost.
* **Options Evaluated**:
  1. *PostgreSQL / SQLite*: Standard open-source choices, but introduce unfamiliar tooling and split dialects between dev and test.
  2. *Microsoft SQL Server Developer / Express Edition + SSMS*: Local Windows-native relational database managed visually via SQL Server Management Studio.
* **Decision / Recommendation**: Adopt **Microsoft SQL Server + SSMS** as the sole primary development and test database.
* **Rationale**: Honors Owner Constraint `CST-CNF-008`. Eliminates learning curve friction; provides enterprise-grade relational features (ACID transactions, indexed views, rich execution plan analysis in SSMS); runs locally at **₹0 cost**.
* **Important Rule**: Do NOT introduce SQLite for testing or PostgreSQL for local dev. All local testing runs against a dedicated local SQL Server database (`StudioWebsiteTest`). Production database remains intentionally decoupled and unfinalized.
* **Cost & Complexity**: ₹0 local license cost for Developer/Express edition.
* **Reversibility**: High via SQLAlchemy 2.x dialect abstraction.

---

### `ADR-005`: ORM & Persistence Layer — SQLAlchemy 2.x & Alembic
* **Status**: `RECOMMENDED`
* **Context**: Need a robust, type-safe data access layer that supports Microsoft SQL Server during development while preserving dialect portability for production.
* **Options Evaluated**:
  1. *Raw SQL / pyodbc scripts*: Full control but zero migration management, high boilerplate, and SQL injection risks.
  2. *SQLAlchemy 2.x (ORM + Core) + Alembic*: Industry-standard Python data mapping library using modern 2.0 select syntax and automated schema versioning.
* **Decision / Recommendation**: Adopt **SQLAlchemy 2.x + Alembic**.
* **Rationale**: Provides complete decoupling from the underlying database dialect; generates fully parameterized queries preventing SQL injection; manages schema evolution via declarative Alembic migrations; and supports both sync (`pyodbc`) and async (`aioodbc`) execution.
* **Cost & Complexity**: Open source, well-documented, zero licensing cost.

---

### `ADR-006`: AI Subsystem Provider Abstraction Layer
* **Status**: `RECOMMENDED`
* **Context**: The AI Discovery engine must integrate with commercial LLM providers without vendor lock-in, rate-limit vulnerability, or unexpected breaking API changes.
* **Options Evaluated**:
  1. *Hardcoded Single Provider SDK (e.g. OpenAI SDK only)*: High risk of lock-in, single point of failure during outages.
  2. *Unified Gateway Interface (LiteLLM or Custom Interface Class)*: A standardized Python interface accepting prompt parameters and returning typed Pydantic objects.
* **Decision / Recommendation**: Adopt a **Unified Python AI Gateway Interface**.
* **Rationale**: Decouples domain logic from specific model providers. Allows instantaneous failover between Google Gemini, Anthropic Claude, and OpenAI without touching discovery business logic.
* **Cost & Complexity**: Adds a thin adapter layer; eliminates vendor lock-in.

---

### `ADR-007`: AI SDK Strategy — Direct Provider SDKs vs. LiteLLM Proxy
* **Status**: `TECHNICAL EVALUATION REQUIRED`
* **Context**: Need to determine whether to use `litellm` Python package as a translation proxy or direct lightweight official SDKs (`google-genai`, `anthropic`, `openai`).
* **Options Evaluated**:
  1. *LiteLLM*: Standardizes input/output across 100+ providers via a single Python call (`completion()`).
  2. *Direct SDKs with Custom Protocol*: Lightweight direct HTTP calls via `httpx` or official SDKs.
* **Decision / Recommendation**: Evaluate **LiteLLM** for local development prototyping, falling back to direct SDK adapters if dependency weight is problematic.
* **Status**: Marked `TECHNICAL EVALUATION REQUIRED`.

---

### `ADR-008`: AI Architecture — Deterministic State Machine vs. Autonomous Multi-Agent Orchestration
* **Status**: `APPROVED BY OWNER (BD-010)`
* **Context**: Must balance high-quality structured discovery synthesis with predictability, speed, low token costs, and zero hallucinated commercial commitments.
* **Options Evaluated**:
  1. *Autonomous Multi-Agent Frameworks (LangChain, CrewAI, AutoGen)*: Agents conversing in unconstrained loops, executing arbitrary web tools.
  2. *Deterministic Finite State Machine + Bounded AI Calls*: Strict, linear workflow states with isolated LLM calls generating typed Pydantic outputs.
* **Decision / Recommendation**: Adopt **Deterministic State Machine + Bounded AI Calls**.
* **Rationale**: Multi-agent swarms introduce compounding latency, unpredictable token cost explosions, debugging opacity, and high hallucination risks. The studio's 7-stage discovery flow has well-defined boundaries that are perfectly modeled by a deterministic state machine.
* **Cost & Complexity**: Vastly lower API token consumption; deterministic reproducibility; 100% testable.

---

### `ADR-009`: Knowledge Retrieval Architecture — Vector Database Necessity
* **Status**: `CONFIRMED (DEC-012, PRD-MVP-004)`
* **Context**: The discovery engine needs access to 30–50 pre-validated studio solution blueprints to match against incoming client problems.
* **Options Evaluated**:
  1. *External Vector Database (Pinecone, Qdrant, Chroma, Weaviate)*: Embedding-based similarity search over external vector stores.
  2. *Curated In-Memory Python Catalog (Dictionary + Heuristic Tag Scoring)*: 30–50 structured solution patterns stored in-memory as typed Pydantic models.
* **Decision / Recommendation**: Adopt **In-Memory Python Catalog with Tag-Based Heuristic Matching for MVP**.
* **Rationale**: A portfolio of 30–50 blueprints does not justify the operational complexity, hosting and licensing costs (Cost Evaluation Required), or latency of an external vector database. Heuristic tag-scoring in Python executes in $< 1\text{ms}$ at ₹0 cost. Vector retrieval (`pgvector`) is deferred to Future horizons.

---

### `ADR-010`: User Identity & Authentication Strategy
* **Status**: `CONFIRMED (BD-005, DEC-014)`
* **Context**: Must provide seamless diagnostic continuity while respecting value-first progressive gating (`BD-005`) and avoiding forced account registration.
* **Options Evaluated**:
  1. *Mandatory Upfront Accounts (Auth0 / Supabase / Cognito)*: Forcing visitors to create a password or social login before exploring discovery.
  2. *Anonymous Session Cookie $\rightarrow$ Magic Link Token Elevation*: Anonymous UUID4 cookie for initial diagnostic; email capture elevates session; magic link restores state.
* **Decision / Recommendation**: Adopt **Anonymous Session Cookie $\rightarrow$ Magic Link Token Elevation**.
* **Rationale**: Maximizes top-of-funnel completion by eliminating password friction. Implemented natively in FastAPI with cryptographic tokens at **₹0 third-party auth cost**.

---

### `ADR-011`: Analytics Telemetry Architecture — Client Telemetry
* **Status**: `RECOMMENDED`
* **Context**: Need funnel telemetry to measure discovery completion rates without compromising client operational privacy or installing invasive third-party tracking cookies.
* **Options Evaluated**:
  1. *Heavy Client Tracking (Google Analytics 4 / Hotjar)*: Invasive tracking cookies, third-party data collection, session replay privacy liabilities.
  2. *Lightweight Anonymous Telemetry Event Bus*: Custom 1KB event dispatcher sending anonymized categorical events (`discovery_started`, `opportunity_map_viewed`) to a server endpoint.
* **Decision / Recommendation**: Adopt **Lightweight Anonymous Event Telemetry**.
* **Rationale**: Designed for zero PII leakage (`BD-014`); eliminates cookie consent banners; maintains high page performance. Vendor selection remains open for technical evaluation.

---

### `ADR-012`: Caching Strategy for MVP
* **Status**: `CONFIRMED (BD-015)`
* **Context**: High-traffic marketing pages require fast delivery, while discovery sessions require real-time dynamic generation.
* **Options Evaluated**:
  1. *Distributed Cache (Redis / Memcached)*: Dedicated caching cluster requiring additional infrastructure and operational maintenance.
  2. *In-Memory Python Caching (`lru_cache`) + HTTP Cache Headers*: Native Python memory caching for static solution blueprints and browser HTTP caching for static assets.
* **Decision / Recommendation**: Adopt **In-Memory Python Caching + HTTP Cache Headers for MVP**.
* **Rationale**: Eliminates Redis hosting costs and local process dependencies (`CST-CNF-008`). Perfectly adequate for MVP traffic.

---

### `ADR-013`: Asynchronous Background Tasks Strategy
* **Status**: `RECOMMENDED`
* **Context**: Email delivery (blueprint delivery, magic links) and internal architect triage alerts must not block user HTTP response cycles.
* **Options Evaluated**:
  1. *Distributed Task Queue (Celery + RabbitMQ/Redis)*: Enterprise-scale worker architecture with heavy broker infrastructure.
  2. *FastAPI Native `BackgroundTasks`*: Lightweight ASGI task runner executing background coroutines within the application process.
* **Decision / Recommendation**: Adopt **FastAPI Native `BackgroundTasks` for MVP**.
* **Rationale**: Eliminates broker infrastructure, running reliably at ₹0 cost. If background task volume expands significantly in Phase 2, a database-backed task queue or Celery can be seamlessly introduced.

---

### `ADR-014`: Production Deployment & Compute Infrastructure
* **Status**: `TBD — DECOUPLED & OPEN (BD-015)`
* **Context**: Development is strictly confirmed as local Uvicorn + MS SQL Server (₹0). Production compute and persistence must be evaluated independently based on scalability, cloud cost, and operational requirements.
* **Options to Evaluate**:
  1. *Linux VPS via Docker Compose (Hetzner / DigitalOcean)*: Self-managed compute (Cost Evaluation Required), full control.
  2. *Managed Container PaaS (Render / Railway / Fly.io)*: PaaS convenience (Cost Evaluation Required), zero server maintenance.
  3. *Enterprise Cloud (AWS / Azure)*: Enterprise services (Cost Evaluation Required), higher operational overhead.
* **Decision**: **Remain Decoupled & Undecided**. No production provider will be selected or provisioned during Phase 4.

---

### `ADR-015`: Observability & Structured Logging
* **Status**: `RECOMMENDED`
* **Context**: Need operational visibility into application errors, AI token usage, database query latencies, and security events without paying for expensive enterprise APM tools.
* **Options Evaluated**:
  1. *Paid SaaS APM (Datadog / New Relic)*: High recurring monthly SaaS subscription cost (Cost Evaluation Required).
  2. *Structured JSON Logging (`structlog`) + Standard System Logs*: Open-source structured logging emitting machine-readable JSON with correlation IDs to standard output.
* **Decision / Recommendation**: Adopt **Structured JSON Logging (`structlog`)**.
* **Rationale**: Generates structured, searchable logs containing `request_id`, `session_id`, and `duration_ms` at ₹0 cost, ready for ingestion by any future log collector.
