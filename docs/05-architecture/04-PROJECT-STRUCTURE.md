# Python Project Structure & Code Organization Specification

**Document ID:** `DOC-ARCH-004`  
**Classification:** System Architecture / Phase 4 Codebase Layout  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [Module Architecture](file:///d:/Project_website/docs/05-architecture/03-MODULE-ARCHITECTURE.md) | [Engineering Conventions](file:///d:/Project_website/docs/05-architecture/25-ENGINEERING-CONVENTIONS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Project Organization Philosophy

In strict accordance with the Python-First hard constraint (`BD-015`, `CST-CNF-007`), the project layout is designed for **maximum readability, clear module boundaries, fast local development, and zero build toolchain bloat**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CODEBASE DESIGN PRINCIPLES                                │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ 1. MODULAR MONOLITH STRUCTURE │ 2. CLEAN SEPARATION OF LAYERS │ 3. ZERO ASSET PIPELINE │
│ Modules self-contained with   │ Controllers ➔ Services ➔      │ Native Jinja2 partials │
│ schemas, routes, & services.  │ Repositories ➔ Models.        │ + static HTMX/Alpine.  │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

## 2. Conceptual Project Directory Blueprint

*(Note: This blueprint specifies the layout required when implementation begins. Zero application code or directories are created in this documentation phase).*

```text
Project_website/
├── docs/                                # Canonical Documentation Repository (Single Source of Truth)
│   ├── 00-project/                      # Governance, Principles, Master Glossary, Registers
│   ├── 01-business/                     # Business Architecture (16 Ratified Foundation Docs)
│   ├── 02-brand/                        # Brand Identity, Voice, Narrative, Guidelines (9 Docs)
│   ├── 03-product/                      # Product Vision, Scoping, AI Discovery Spec (13 Docs)
│   ├── 04-website/                      # Website Strategy, Sitemap, UX, SEO, Wireframes (19 Docs)
│   └── 05-architecture/                 # Engineering Specifications, ADRs, Database, AI (30 Docs)
│
├── app/                                 # Core Python Application Package
│   ├── __init__.py
│   ├── main.py                          # FastAPI Application Factory & Ingress Assembly
│   ├── config.py                        # Pydantic-Settings Configuration (.env loader)
│   │
│   ├── shared/                          # Universal Shared Foundation (No Domain Logic)
│   │   ├── __init__.py
│   │   ├── exceptions.py                # Base Custom Domain Exceptions & Envelopes
│   │   ├── logging.py                   # Structured JSON Logger Configuration (structlog)
│   │   ├── security.py                  # Cryptographic Token Signers & PII Scrubbers
│   │   └── utils.py                     # Date, Time, and String Helpers
│   │
│   ├── database/                        # Persistence Layer (SQLAlchemy 2.x & MS SQL Server)
│   │   ├── __init__.py
│   │   ├── connection.py                # Engine, Connection Pool, and Sessionmaker
│   │   ├── base.py                      # Declarative Base & Audit Columns Mixin
│   │   └── session.py                   # FastAPI Database Session Dependency
│   │
│   ├── ai_gateway/                      # External AI Integration Subsystem
│   │   ├── __init__.py
│   │   ├── client.py                    # Provider Client Abstraction (LiteLLM / SDKs)
│   │   ├── prompts.py                   # Version-Controlled Prompt Templates
│   │   ├── extractor.py                 # Structured Output Pydantic Extraction Engine
│   │   └── safety.py                    # Prompt Injection Defenses & Sanitizers
│   │
│   ├── content/                         # Static Catalog & Template Models
│   │   ├── __init__.py
│   │   ├── pillars.py                   # 5 Service Pillar In-Memory Data Models
│   │   ├── solutions.py                 # Pre-Validated Solution Blueprint Catalog
│   │   └── service.py                   # Content Retrieval Service
│   │
│   ├── modules/                         # Core Business Domain Modules
│   │   ├── web/                         # Public Marketing Web Views
│   │   │   ├── __init__.py
│   │   │   └── router.py                # Routes for Home, Services, Solutions, About, Legal
│   │   │
│   │   ├── discovery/                   # AI Project Discovery Engine
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # HTMX Stepper Endpoints (/api/discovery/*)
│   │   │   ├── state_machine.py         # Deterministic Finite State Machine Logic
│   │   │   ├── service.py               # Intake Orchestration & Session Coordinator
│   │   │   ├── models.py                # SQLAlchemy Models (discovery_sessions, stages)
│   │   │   └── schemas.py               # Pydantic DTOs for Discovery Requests/Responses
│   │   │
│   │   ├── opportunity/                 # Opportunity Mapping Engine
│   │   │   ├── __init__.py
│   │   │   ├── service.py               # Categorization & Scoring Algorithm
│   │   │   ├── models.py                # SQLAlchemy Models (opportunities, categories)
│   │   │   └── schemas.py               # Pydantic OpportunityDTOs
│   │   │
│   │   ├── blueprint/                   # Solution Blueprint Engine
│   │   │   ├── __init__.py
│   │   │   ├── service.py               # 18-Section Blueprint Assembly
│   │   │   ├── models.py                # SQLAlchemy Models (solution_blueprints, sections)
│   │   │   └── schemas.py               # Pydantic SolutionBlueprintDTO
│   │   │
│   │   ├── estimation/                  # Indicative Sizing Engine
│   │   │   ├── __init__.py
│   │   │   ├── service.py               # Deterministic Budget & Timeline Sizing Formula
│   │   │   ├── models.py                # SQLAlchemy Models (estimates, factors)
│   │   │   └── schemas.py               # Pydantic EstimateDTO & Disclaimers
│   │   │
│   │   ├── leads/                       # Lead Capture & Progressive Gating
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # Lead Capture POST Endpoint
│   │   │   ├── service.py               # Validation, Session Elevation, Consent Tracking
│   │   │   ├── models.py                # SQLAlchemy Models (leads, consents)
│   │   │   └── schemas.py               # Pydantic LeadCaptureDTO
│   │   │
│   │   ├── review/                      # Human Architect Review & Triage
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # Review Request & Architect Triage Endpoints
│   │   │   ├── service.py               # Triage Queue & Evaluation Annotation
│   │   │   ├── models.py                # SQLAlchemy Models (review_requests, decisions)
│   │   │   └── schemas.py               # Pydantic ReviewDTO
│   │   │
│   │   ├── auth/                        # Identity & Session Management
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py          # Cookie-to-Session FastAPI Dependency
│   │   │   └── service.py               # Cryptographic Signing & Magic Link Generation
│   │   │
│   │   └── notifications/               # Background Alerts & Email
│   │       ├── __init__.py
│   │       ├── email.py                 # SMTP / Transactional Email Dispatcher
│   │       └── service.py               # Client Confirmation & Architect Alert Routines
│   │
│   ├── templates/                       # Jinja2 Server-Side HTML Templates
│   │   ├── layouts/                     # Base Skeletons (base.html, discovery_layout.html)
│   │   ├── pages/                       # Full Canonical Pages (index, services, about, contact)
│   │   ├── components/                  # Global Macro Components (nav, footer, cards, badges)
│   │   └── partials/                    # Dynamic HTMX Swaps (stage_1, stage_2, map, blueprint)
│   │
│   └── static/                          # Static Frontend Assets (Zero Build Pipeline)
│       ├── css/                         # Vanilla CSS Design System (index.css, tokens.css)
│       ├── js/                          # Vendor Scripts (htmx.min.js, alpine.min.js)
│       ├── images/                      # SVG Icons, Diagrams, Brand Marks
│       └── robots.txt                   # Search Engine Indexing Directives
│
├── migrations/                          # Alembic Database Migration Scripts
│   ├── versions/                        # Sequential Python Migration Files
│   ├── env.py                           # Alembic Database Context (Configured for SQL Server)
│   └── script.py.mako                   # Migration Script Template
│
├── tests/                               # Comprehensive Automated Test Suite
│   ├── conftest.py                      # Universal Pytest Fixtures & SQL Server Test DB Setup
│   ├── unit/                            # Pure Domain Logic & Sizing Formula Tests
│   ├── integration/                     # SQLAlchemy Repository & Database Operations
│   ├── api/                             # FastAPI TestClient HTTP Contract Assertions
│   ├── ai/                              # Mocked LLM Extraction & Schema Validation Tests
│   └── e2e/                             # End-to-End User Journey Simulation
│
├── .env.example                         # Template for Environment Configuration Variables
├── alembic.ini                          # Alembic Migration Configuration File
├── pyproject.toml                       # Python Packaging, Dependencies, and Linter Config
└── requirements.txt                     # Pinned Production & Development Dependencies
```

---

## 3. Layer Separation & Responsibilities Within Modules

Every domain module in `app/modules/[name]/` follows a strict 4-layer internal architecture:
1. **`router.py` (Controller Layer)**: Pure FastAPI HTTP routing, request binding, cookie extraction, status code mapping, and Jinja2/HTMX response triggering. Contains **zero business logic**.
2. **`service.py` (Domain Service Layer)**: Orchestrates business rules, enforces domain constraints, coordinates transactions, and transitions state machines.
3. **`models.py` (Persistence Layer)**: Declarative SQLAlchemy 2.x ORM models representing database tables in Microsoft SQL Server.
4. **`schemas.py` (Data Contract Layer)**: Pydantic v2 schemas defining input validation rules and output DTOs.
