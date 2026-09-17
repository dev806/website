# Data Flow Architecture & Information Lifecycle

**Document ID:** `DOC-ARCH-007`  
**Classification:** System Architecture / Phase 4 Data Engineering  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Database Schema Spec](file:///d:/Project_website/docs/05-architecture/06-DATABASE-SCHEMA-SPEC.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Data Flow Architecture Principles

Every data stream within `[STUDIO_NAME]` adheres to four strict engineering laws:
1. **Data Minimization Law**: Only data strictly required for immediate architectural synthesis and contact fulfillment is captured.
2. **Sanitization Precedence**: Untrusted client inputs are sanitized, scrubbed of PII, and validated via Pydantic v2 before hitting database persistence or external AI APIs.
3. **Auditability & Traceability**: Critical commercial state transitions (lead gating, review requests, estimate outputs) leave an immutable audit trail in Microsoft SQL Server.
4. **Resilient Failure Boundaries**: Failures at any external boundary (e.g. AI provider outage) degrade gracefully to pre-validated deterministic fallbacks without breaking the user session.

---

## 2. Comprehensive Data Flow Specifications (Flows A through H)

---

### Flow A: Visitor $\rightarrow$ Website $\rightarrow$ Discovery Session Initialization
* **Source**: Web browser navigating to `/discovery` or clicking *"Start With Your Problem"*.
* **Transformation**: FastAPI `AuthService` inspects incoming request for session cookie. If absent, issues a cryptographically signed UUID4 session cookie (`HttpOnly`, `SameSite=Lax`).
* **Storage**: Initial `DiscoverySession` record inserted into `dbo.discovery_sessions` with status `'START'`.
* **Destination**: Jinja2 renders `/templates/pages/discovery.html` with initial Stage 1 input partial.
* **Security Boundary**: Public untrusted ingress $\rightarrow$ Application runtime.
* **PII & Retention**: Zero PII collected. Anonymous sessions purged via automated sweeper according to data retention policy (`POLICY DECISION REQUIRED`).
* **Failure Handling**: If database write fails, session falls back to client-side `localStorage` state with delayed server synchronization.

---

### Flow B: Problem Input $\rightarrow$ AI Processing $\rightarrow$ Structured Understanding
* **Source**: User submits natural language problem textarea in Stage 1.
* **Transformation**:
  1. FastAPI controller validates input length ($\ge 20$ chars).
  2. `SecurityService` scrubs sensitive credentials and credit cards.
  3. `AIGateway` formats prompt with Pydantic target schema (`StructuredProblemContextDTO`).
  4. External LLM returns structured JSON; Pydantic validates schema types.
* **Storage**: Record inserted into `dbo.problem_statements` and `dbo.structured_contexts`.
* **Destination**: Jinja2 renders `stage_2_questions.html` swapped into browser DOM via HTMX.
* **Security Boundary**: Application runtime $\rightarrow$ External AI Provider (Encrypted TLS, Zero-Retention Enterprise API Terms, `BD-014`).
* **Failure Handling**: If external LLM times out ($>10$s), engine retries once, then falls back to a deterministic heuristic question set based on keyword matching.

---

### Flow C: Structured Understanding $\rightarrow$ Opportunity Map Generation
* **Source**: User answers Stage 2 clarification questions and advances to Stage 4.
* **Transformation**:
  1. `OpportunityService` maps problem context and question answers against the 5 opportunity categories (Quick Wins, Core Builds, Automation, Integrations, System Risks).
  2. Assigns qualitative impact and complexity ratings using deterministic heuristic rules.
* **Storage**: Opportunity records inserted into `dbo.opportunities`.
* **Destination**: Jinja2 renders `stage_4_opportunity_map.html` in browser.
* **Security Boundary**: Internal application memory $\rightarrow$ SQL Server.
* **Reciprocal Value Milestone**: **100% Free & Ungated output (`BD-005`)**.
* **Failure Handling**: Deterministic algorithmic mapping ensures 100% availability without external API dependency.

---

### Flow D: Opportunity Map $\rightarrow$ Solution Blueprint Generation
* **Source**: Client unlocks Stage 5 by submitting contact details at the lead gate.
* **Transformation**:
  1. `BlueprintService` queries validated opportunities and matches them against pre-curated studio architectural patterns (`app/content/solutions.py`).
  2. Synthesizes 18 canonical blueprint sections, applying the mandatory visual status badge `[✦ AI-Generated Preliminary Draft]`.
* **Storage**: Master record created in `dbo.solution_blueprints` and 18 rows inserted into `dbo.blueprint_sections`.
* **Destination**: Rendered as expandable accordion UI on client screen.
* **Security Boundary**: Application domain $\rightarrow$ SQL Server transaction boundary.
* **Failure Handling**: Asynchronous rendering with skeleton loaders; database transaction rolled back if section generation fails.

---

### Flow E: Blueprint $\rightarrow$ Indicative Sizing Estimation
* **Source**: Input complexity signals, integration count, data scale tier.
* **Transformation**:
  1. `EstimationService` computes low-to-high budget bands (INR & USD) and timeline durations using the approved deterministic formula (`BD-006`).
  2. Embeds the immutable mandatory legal disclaimer string.
* **Storage**: Record inserted into `dbo.estimates`.
* **Destination**: Displayed on Stage 6 estimation dashboard.
* **Security Boundary**: Pure deterministic Python logic (Zero unconstrained AI hallucination risks).
* **Failure Handling**: Default sizing baseline applied if specific input signals are ambiguous, flagged with `Confidence: LOW`.

---

### Flow F: Progressive Lead Capture $\rightarrow$ Architect Review Triage
* **Source**: User enters Name and Corporate Email on Stage 5 progressive reveal gate.
* **Transformation**:
  1. `LeadService` validates email syntax, normalizes domain, and records explicit consent timestamp.
  2. Links newly created `Lead` record to the existing `DiscoverySession`.
* **Storage**: Inserted into `dbo.leads` and `dbo.lead_consents`.
* **Destination**: Triggers session unlock; dispatches internal review alert.
* **Security Boundary**: User PII encrypted at rest; email never exposed to client-side trackers.
* **Failure Handling**: Duplicate email submissions update the existing lead record without throwing client-facing errors.

---

### Flow G: Human Review Bridge $\rightarrow$ Client Engagement (`BD-010`)
* **Source**: User clicks *"Request Human Architect Review"* on Stage 7.
* **Transformation**: Creates a prioritized triage ticket in `dbo.review_requests`; dispatches internal notification via FastAPI `BackgroundTasks`.
* **Storage**: `ReviewRequest` created with status `'PENDING'`.
* **Destination**: Senior architect dashboard / notification queue.
* **Human Action**: Architect inspects the brief, validates technical assumptions, verifies third-party API constraints, and prepares a formal Proposal / Discovery Sprint offer within 1 business day (`BD-013`).
* **Security Boundary**: Internal architect access protected by role-based authorization.

---

### Flow H: Anonymous Client Telemetry $\rightarrow$ Aggregate Analytics
* **Source**: Browser UI event triggers (`discovery_started`, `opportunity_map_viewed`).
* **Transformation**: Alpine.js dispatches non-blocking JSON payload via `navigator.sendBeacon`.
* **Destination**: Internal telemetry collector endpoint.
* **PII Safeguard**: **Zero PII captured (`BD-014`)**. Telemetry excludes email, name, and problem text. Uses pseudorandom session hashes solely for funnel drop-off calculation.
* **Retention**: Raw telemetry purged according to data retention policy schedule (`POLICY DECISION REQUIRED`); aggregated anonymous metrics retained for conversion analysis.
