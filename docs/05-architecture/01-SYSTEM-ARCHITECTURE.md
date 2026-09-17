# System Architecture Specification: The Modular Studio Monolith

**Document ID:** `DOC-ARCH-001`  
**Classification:** System Architecture / Phase 4 Foundational Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-008](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-008), [BD-009](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-009), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-011](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-011), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [Technology Decision Framework](file:///d:/Project_website/docs/00-project/TECHNOLOGY_DECISION_FRAMEWORK.md) | [Website Strategy](file:///d:/Project_website/docs/04-website/01-WEBSITE-STRATEGY.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. System Purpose & Strategic Mandate

The system architecture of `[STUDIO_NAME]` powers a unified, high-craft digital operating platform fulfilling two core mandates:
1. **The Trust & Positioning Anchor**: Delivers lightning-fast, server-rendered marketing and capability pages validating the studio's category leadership as an AI-native technology partner (`BD-009`, `BD-011`).
2. **The Product-Led AI Discovery Engine**: Provides an interactive, deterministic cognitive intake experience (*"Start With Your Problem"*, `BD-012`) translating unstructured business problems into Opportunity Maps, Solution Blueprints, and indicative estimates without requiring clients to possess technical expertise.

The architecture is deliberately engineered as a **Python-First Modular Monolith** (`BD-015`, `CST-CNF-007`) running locally on **Microsoft SQL Server + SSMS** at **₹0 infrastructure cost** (`CST-CNF-008`), eliminating premature microservice and cloud hosting bloat.

---

## 2. Macro Architecture Diagram

```mermaid
graph TD
    subgraph Client_Layer["Client Layer (Browser)"]
        HTML["Server-Rendered HTML5 / CSS (Jinja2)"]
        HTMX["HTMX (DOM Morphing & Async Swaps ~14KB)"]
        Alpine["Alpine.js (Lightweight Client State ~15KB)"]
        Storage["Browser LocalStorage (Draft Continuity)"]
    end

    subgraph Edge_Reverse_Proxy["Local Dev / Ingress"]
        Uvicorn["Uvicorn ASGI Server (:8000) (Hot Reload)"]
    end

    subgraph Application_Core["FastAPI Modular Monolith (Python 3.12+)"]
        MW["Middleware (RequestID, RateLimit, CSRF, Security Headers)"]
        Router["FastAPI Application Router"]
        
        subgraph Functional_Modules["Domain Modules (Decoupled Boundaries)"]
            Mod_Web["Web & Marketing Module"]
            Mod_Disc["AI Discovery State Machine Module"]
            Mod_Opp["Opportunity Mapping Module"]
            Mod_Blue["Solution Blueprint Module"]
            Mod_Est["Estimation Engine Module"]
            Mod_Lead["Lead Management & Gating Module"]
            Mod_Rev["Human Architect Review Module"]
        end
        
        subgraph Core_Services["Core & Infrastructure Services"]
            Pydantic["Pydantic v2 (Strict Schema Validation)"]
            AIGateway["AI Gateway (LiteLLM / Direct Provider SDKs)"]
            TaskEngine["FastAPI BackgroundTasks (Async Email/Alerts)"]
            AuditLogger["Structured JSON Logger (Audit Trail)"]
        end
        
        subgraph Persistence_Layer["Data Access Layer"]
            SQLA["SQLAlchemy 2.x ORM / Core (Unit of Work)"]
            Alembic["Alembic Migrations Engine"]
        end
    end

    subgraph Data_Storage["Development Database Infrastructure (CST-CNF-008)"]
        MSSQL["Microsoft SQL Server (Developer / Express Edition)"]
        SSMS["SQL Server Management Studio (SSMS Management GUI)"]
    end

    subgraph External_AI_APIs["External AI Provider Boundary (BD-014)"]
        LLM["Candidate AI Provider (Provider Evaluation Required)"]
    end

    Client_Layer <-->|HTTP GET/POST, Partial Swaps| Edge_Reverse_Proxy
    Edge_Reverse_Proxy <--> Uvicorn
    Uvicorn --> MW --> Router
    Router --> Functional_Modules
    Functional_Modules --> Core_Services
    Functional_Modules --> Persistence_Layer
    Core_Services <-->|TLS REST (Evaluated Non-Training Terms)| External_AI_APIs
    Persistence_Layer <-->|ODBC Driver 18 (pyodbc / aioodbc)| Data_Storage
    SSMS -.->|Local Admin / Inspection| MSSQL
```

---

## 3. Core Architectural Lifecycles

### A. HTTP Request & Interaction Lifecycle
1. **Client Interaction**: Visitor clicks a trigger (e.g. submitting problem text in `/discovery`). HTMX intercepts the form submission, issuing an asynchronous `hx-post="/api/discovery/problem"` request with current form state.
2. **Ingress & Middleware Execution**:
   - `CorrelationIdMiddleware`: Injects a unique `X-Request-ID` (UUID4) into request state and logging context.
   - `SecurityHeadersMiddleware`: Enforces `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and restrictive `Content-Security-Policy`.
   - `RateLimitingMiddleware`: Enforces client IP throttling on discovery endpoints to prevent API abuse.
3. **Routing & Pydantic Validation**: FastAPI routes the payload to the Discovery controller; Pydantic v2 validates input types, character bounds ($\ge 20$ chars), and sanitizes untrusted input.
4. **Domain Execution & State Machine**: The Discovery domain service transitions the session state (`START` $\rightarrow$ `PROBLEM_CAPTURED`), invokes the AI Gateway for structured classification, and updates the session entity.
5. **Persistence Unit of Work**: SQLAlchemy opens a transactional session against Microsoft SQL Server, executes parameterized queries via ODBC, and commits the state.
6. **Server-Side Template Morphing**: Jinja2 renders only the requested HTML fragment (`stage_2_questions.html`), returning a partial response. HTMX swaps this fragment into the DOM within $< 150\text{ms}$ without a full browser page refresh.

### B. User Identity & Session Continuity Lifecycle
```
[Anonymous Visitor] ──➔ Generates UUID4 Session Cookie (HttpOnly, SameSite=Lax)
       │
       ▼
[Problem Intake] ────➔ Draft persisted to Client LocalStorage + Server DB (Policy-governed purge)
       │
       ▼
[Lead Capture Gate] ──➔ User enters Name & Corporate Email to unlock Blueprint
       │
       ▼
[Lead Elevation] ────➔ Session elevated: Linked to Lead record in SQL Server
       │
       ▼
[Recovery Access] ───➔ Magic Link Token generated; user can resume diagnostic across devices
```

### C. AI Discovery Lifecycle & State Progression
The discovery engine operates as a **strictly bounded deterministic finite state machine** (`DOC-ARCH-011`). It does not run unbounded autonomous loops. Every AI invocation is an isolated, structured classification or synthesis task strictly bound to typed Pydantic output schemas.

### D. Human Review Lifecycle (The 5 Mandatory Human Gates, `BD-010`)
1. **Gate 1 (Blueprint Inspection)**: Preliminary AI-generated blueprints are flagged with `[✦ AI-Generated Preliminary Draft]`.
2. **Gate 2 (Architect Review Request)**: When a client clicks *"Request Human Architect Review"*, a `ReviewRequest` entity is created in SQL Server, and an alert is dispatched via FastAPI `BackgroundTasks`.
3. **Gate 3 (Feasibility Validation)**: A senior human architect evaluates the technical architecture, verifies API limits, and manually endorses or edits the brief.
4. **Gate 4 (Commercial Proposal Sign-Off)**: Human architects independently calculate pricing, duration, and Statements of Work (SOW). Automated estimates (`BD-006`) are strictly non-binding.
5. **Gate 5 (Contractual Commitment)**: Only signed human contracts authorize production code delivery.

---

## 4. Subsystem & Module Boundaries

The application is structured as a **Modular Monolith** where domain logic is compartmentalized into discrete Python packages with strict boundary rules:

| Module Name | Primary Responsibility | Data Entities Owned | Inbound Dependencies | Forbidden Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **`web`** | Marketing routes, static views, global layouts, SEO sitemaps. | Static Content Dictionaries | `shared`, `content` | `ai`, `estimation` (Directly) |
| **`discovery`** | Session management, 7-stage state machine, problem intake. | `DiscoverySession`, `DiscoveryStage` | `shared`, `ai`, `database` | `leads` (Directly; uses events) |
| **`opportunity`** | Opportunity categorization, impact/complexity mapping. | `Opportunity`, `OpportunityCategory` | `shared`, `discovery` | `notifications` |
| **`blueprint`** | 18-section architectural blueprint synthesis & presentation. | `SolutionBlueprint`, `BlueprintSection`| `shared`, `discovery`, `ai` | `leads` |
| **`estimation`** | Non-binding budget/timeline sizing algorithm (`BD-006`). | `Estimate`, `EstimateFactor` | `shared`, `discovery` | `ai` (Direct unconstrained calls) |
| **`leads`** | Progressive capture, contact verification, consent (`BD-005`). | `Lead`, `LeadConsent` | `shared`, `database` | `ai` |
| **`review`** | Human architect triage queue, manual evaluation notes (`BD-010`). | `ReviewRequest`, `ReviewDecision` | `shared`, `leads`, `blueprint` | `web` |
| **`ai_gateway`** | Provider abstraction, structured extraction, retries, safety. | None (Stateless Gateway) | `shared` | `database`, `web` |
| **`database`** | SQLAlchemy connection pooling, engine setup, Alembic models. | Master Database Engine | `shared` | Domain business logic |

---

## 5. Security & Trust Perimeters

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY PERIMETER BOUNDARIES                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PERIMETER 1: PUBLIC UNTRUSTED BOUNDARY (Browser ➔ Ingress)                             │
│ • Cloudflare/Nginx reverse proxy terminates TLS (Production).                          │
│ • Localhost Uvicorn binding (Development).                                             │
│ • Input payload length limits (Max 20KB for discovery text).                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PERIMETER 2: APPLICATION RUNTIME BOUNDARY (FastAPI Controllers)                        │
│ • Strict Pydantic input sanitization and PII masking.                                  │
│ • CSRF token validation on all state-mutating POST requests.                           │
│ • Rate limiting on LLM extraction endpoints (Max 5 requests/min per session).          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PERIMETER 3: PERSISTENCE BOUNDARY (SQLAlchemy ➔ Microsoft SQL Server)                  │
│ • 100% Parameterized queries via SQLAlchemy ORM (Zero raw string concatenation).       │
│ • Dedicated database user with least-privilege DDL/DML permissions.                    │
│ • Encrypted connection strings via environment variables (`pydantic-settings`).       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PERIMETER 4: THIRD-PARTY AI BOUNDARY (AI Gateway ➔ External LLM Provider)              │
│ • Zero-retention enterprise API terms enforced (`BD-014`).                             │
│ • Automated client-side PII scrubbing prior to transit.                                │
│ • Strict schema enforcement preventing prompt injection data leakage.                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Development vs. Production Topology (`BD-015`)

In strict accordance with `CST-CNF-008`, development and production environments optimize for different objectives while sharing identical Python domain code:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ DEVELOPMENT ENVIRONMENT (CONFIRMED CST-CNF-008)                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • OS: Windows 11 Workstation                                                           │
│ • Server: Uvicorn ASGI (`--reload`) on localhost:8000 (₹0 infrastructure cost)        │
│ • Database: Microsoft SQL Server Developer/Express Edition (Localhost:1433)            │
│ • Management: SQL Server Management Studio (SSMS) for visual schema inspection         │
│ • Driver: Microsoft ODBC Driver 18 for SQL Server via `pyodbc` / `aioodbc`             │
│ • External Cloud Services: None required for local runtime                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PRODUCTION ENVIRONMENT (INTENTIONALLY OPEN & DECOUPLED)                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Compute: Undecided (To be evaluated in Phase 4: Linux VPS vs Container PaaS)         │
│ • Database: Undecided (To be evaluated: Managed Cloud SQL Server vs Linux SQL vs PG)  │
│ • Ingress: Reverse Proxy (Caddy / Nginx) with automated Let's Encrypt TLS              │
│ • Architecture Conformance: Domain logic remains 100% database-dialect agnostic via   │
│   SQLAlchemy 2.x abstraction layers.                                                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
