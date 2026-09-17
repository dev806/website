# System Traceability Matrix (Requirements to Architecture)

**Document ID:** `DOC-ARCH-027`  
**Classification:** Systems Engineering / Phase 4 Traceability Canon  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001) through [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Requirements Register](file:///d:/Project_website/docs/00-project/REQUIREMENTS_REGISTER.md) | [Website Requirements](file:///d:/Project_website/docs/04-website/17-WEBSITE-REQUIREMENTS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Traceability Methodology

This matrix establishes an unbroken, bidirectional verification chain across all project layers:
$$\text{Business Decisions (BD)} \longleftrightarrow \text{Product Requirements (PRD)} \longleftrightarrow \text{Website Requirements (WEB)} \longleftrightarrow \text{Architecture / DB / API} \longleftrightarrow \text{Tests}$$

---

## 2. Master Traceability Matrix (Core MVP System)

| Business / Product Req | Website Requirement | Architecture Module | Database Entity | API Contract | Security / QA Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`BD-001`** (Brand Name Placeholder) | `WEB-REQ-001`, `WEB-REQ-002` | `app/config.py`, `app/modules/web` | `dbo.discovery_sessions` | Global Headers / Views | Verified via static audit; `[STUDIO_NAME]` parameterized. |
| **`BD-002`** (Target Segments: Startups/SMEs) | `WEB-REQ-001`, `WEB-REQ-011` | `app/content/pillars.py`, `app/modules/web` | N/A (Static Catalog) | `GET /solutions`, `GET /services/*` | Verified via content review and persona path tests. |
| **`BD-003`** (India-first $\rightarrow$ Global) | `WEB-REQ-007`, `WEB-REQ-011` | `app/modules/estimation` | `dbo.estimates (budget_inr/usd)`| `GET /api/v1/discovery/estimate` | `test_estimation_currency_parity()` asserts dual pricing bands. |
| **`BD-004`** (Free Diag $\rightarrow$ Paid Sprint) | `WEB-REQ-002`, `WEB-REQ-023` | `app/modules/discovery`, `app/modules/review` | `dbo.review_requests` | `POST /api/v1/discovery/review` | `test_discovery_sprint_interest()` asserts telemetry tracking. |
| **`BD-005`** (Value-First Progressive Gating) | `WEB-REQ-005`, `WEB-REQ-006` | `app/modules/leads`, `app/modules/discovery` | `dbo.leads`, `dbo.discovery_sessions` | `POST /api/v1/discovery/lead-unlock` | `test_gate_security()` asserts Stage 4 is free, Stage 5 gated. |
| **`BD-006`** (Non-Binding Estimation Bands) | `WEB-REQ-007`, `WEB-REQ-008` | `app/modules/estimation` | `dbo.estimates` | `GET /api/v1/discovery/estimate` | `test_mandatory_disclaimer()` asserts immutable legal disclaimer. |
| **`BD-008`** (Services to Products Evolution) | `WEB-REQ-011`, `WEB-REQ-025` | `app/content/solutions.py` | `dbo.solution_blueprints` | `GET /solutions` | Content models map reusable architecture patterns. |
| **`BD-009`** (AI-Native Studio Positioning) | `WEB-REQ-001`, `WEB-REQ-010` | `app/modules/web` | N/A (Static Templates) | `GET /`, `GET /services` | Homepage 9-section narrative reflects studio positioning. |
| **`BD-010`** (AI Leverage, Humans Judgement) | `WEB-REQ-009`, `WEB-REQ-012` | `app/modules/review`, `app/ai_gateway` | `dbo.review_requests`, `dbo.blueprint_sections` | `POST /api/v1/discovery/review` | Status badges (`AI Draft` vs `Architect Endorsed`) verified. |
| **`BD-011`** (North Star & Core Promise) | `WEB-REQ-001`, `WEB-REQ-003` | `app/modules/discovery` | `dbo.problem_statements` | `POST /api/v1/discovery/problem` | `test_problem_intake()` asserts plain-English processing. |
| **`BD-012`** (Primary CTA: "Start Problem") | `WEB-REQ-001`, `WEB-REQ-016` | `app/modules/web`, `templates/` | N/A (Templates) | Universal CTA Button | Layout tests verify persistent mobile conversion bar. |
| **`BD-013`** (Turnaround Target, No Public SLA) | `WEB-REQ-009`, `WEB-REQ-013` | `app/modules/review` | `dbo.review_requests` | `POST /api/v1/discovery/review` | Triage time policy verified; zero contractual SLA claims. |
| **`BD-014`** (Privacy & Non-Training Terms) | `WEB-REQ-014`, `WEB-REQ-020` | `app/shared/security.py`, `app/ai_gateway` | `dbo.problem_statements (sanitized)` | Outbound AI Gateway Calls | `test_pii_scrubber()` asserts sensitive patterns redacted; provider terms evaluation required. |
| **`BD-015`** (Python-First, MS SQL Server, ₹0) | `WEB-REQ-015`, `WEB-REQ-022` | `app/database/`, `app/main.py` | Microsoft SQL Server (`dbo.*`) | FastAPI ASGI Server | Integration tests run against local `StudioWebsiteTest` DB. |
| **`PRD-REQ-001`** (Natural Problem Input) | `WEB-REQ-003` | `app/modules/discovery` | `dbo.problem_statements` | `POST /api/v1/discovery/problem` | `test_minimum_character_length()` asserts $\ge 20$ chars. |
| **`PRD-REQ-002`** (Clarification Questions) | `WEB-REQ-004` | `app/modules/discovery` | `dbo.structured_contexts` | `POST /api/v1/discovery/answers` | `test_question_generation()` asserts 3–5 adaptive questions. |
| **`PRD-REQ-003`** (Executive Opportunity Map) | `WEB-REQ-005` | `app/modules/opportunity` | `dbo.opportunities` | `GET /api/v1/discovery/opportunity-map` | Asserts 5 opportunity categories with impact/complexity. |
| **`PRD-REQ-004`** (18-Section Solution Blueprint) | `WEB-REQ-006` | `app/modules/blueprint` | `dbo.solution_blueprints`, `sections` | `GET /api/v1/discovery/blueprint` | Asserts all 18 canonical sections generated and stored. |
| **`PRD-REQ-009`** (Session Draft Recovery) | `WEB-REQ-021` | `app/modules/auth` | `dbo.discovery_sessions` | `GET /discovery/review?token=...`| `test_magic_link_redemption()` asserts session restoration. |
| **`PRD-REQ-011`** (WCAG 2.1 AA Accessibility) | `WEB-REQ-017`, `WEB-REQ-018` | `templates/` | N/A (Frontend Templates) | HTML5 Layouts | Contrast ratio tests ($\ge 4.5:1$) and 48px touch targets verified. |
| **`PRD-REQ-012`** (Lean Anonymous Telemetry) | `WEB-REQ-020` | `app/modules/analytics` | N/A (Telemetry Stream) | Telemetry Dispatches | Asserts zero PII transmitted in telemetry payloads. |
