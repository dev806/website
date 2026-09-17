# Website Content Architecture & Data Models

**Document ID:** `DOC-WEB-010`  
**Classification:** Website Architecture / Phase 3 Content Architecture  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-008](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-008), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Information Architecture](file:///d:/Project_website/docs/04-website/03-INFORMATION-ARCHITECTURE.md) | [Page Specifications](file:///d:/Project_website/docs/04-website/04-PAGE-SPECIFICATIONS.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Content Governance & MVP Architecture

In strict accordance with the Python-First Architecture (`BD-015`) and MVP scoping decisions (`PRD-MVP-002`), **a headless CMS is strictly excluded from MVP scope**. Introducing Strapi, Sanity, or Contentful would add external dependencies, build pipelines, and ongoing cloud costs without providing user value at launch.

All MVP content is cleanly organized into **version-controlled Python data models and Jinja2 modular partials**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CONTENT TAXONOMY & LIFECYCLE                              │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ CONTENT TYPE          │ STORAGE & RENDERING MODE   │ EDITORIAL / UPDATE CADENCE        │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Marketing & Narrative │ Static Jinja2 Partials     │ High stability; code-reviewed     │
│ (Home, About, Trust)  │ (server-side rendered)     │ Git commits.                      │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Services & Blueprints │ Structured Python Data     │ Curated dictionary catalog        │
│ (5 Pillars, 9 Models) │ Schemas (Pydantic models)  │ updated with new studio patterns. │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Discovery Diagnostics │ Dynamic LLM Synthesis      │ Ephemeral session data with       │
│ (Map, Blueprint, Est) │ + Pydantic v2 validation   │ anonymous database persistence.   │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Legal & Governance    │ Static Markdown/HTML       │ Legal review; strictly versioned. │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 2. Structured Content Models

### A. Service Pillar Content Model (`ServicePillarModel`)
* **`id`**: String (e.g. `"software"`, `"ai"`, `"automation"`, `"integrations"`, `"scale"`).
* **`title`**: String (e.g. `"Custom Software Engineering"`).
* **`tagline`**: String (e.g. `"High-craft full-stack web applications and internal tools."`).
* **`core_problems_solved`**: List of Strings (acute operational frictions addressed).
* **`architectural_capabilities`**: List of Strings (technical capabilities).
* **`stack_baseline`**: List of Strings (e.g. Python, FastAPI, SQLAlchemy, background queues).
* **`discovery_preseed_topic`**: String (passed as query param into `/discovery`).

### B. Solution Blueprint Content Model (`SolutionBlueprintModel`)
* **`id`**: String (e.g. `"workflow-consolidation"`).
* **`name`**: String (e.g. `"Operational Workflow Consolidation"`).
* **`target_segment`**: List of Enum (`"Startup"`, `"SME"`, `"Growing Business"`).
* **`symptom_pattern`**: String (business problem scenario).
* **`architecture_pattern`**: String (recommended systems design).
* **`key_outcomes`**: List of Strings (business results delivered).
* **`estimated_effort_band`**: String (e.g. `"4 – 8 Weeks"`).

### C. AI Discovery Session Content Model (`DiscoverySessionModel`)
* **`session_id`**: UUID4 (unique session identifier).
* **`raw_problem_input`**: Text (user's natural language problem).
* **`clarification_answers`**: Key-value JSON dictionary of selected options.
* **`opportunity_map_data`**: Structured JSON array of opportunity nodes (Class, Title, Rationale, Complexity, Impact).
* **`solution_blueprint_data`**: Structured JSON containing the 18-section architectural draft.
* **`indicative_estimate_data`**: Structured JSON containing budget range, timeline band, confidence rating, and disclaimer.
* **`lead_contact`**: Optional Object (Name, Email, Company Name, Consent Timestamp).
* **`status`**: Enum (`"draft"`, `"unlocked"`, `"review_requested"`).

---

## 3. Content Classification: AI-Generated vs. Human-Approved

Every content block rendered on the website belongs to an explicit governance classification:

1. **Static Studio Content**: 100% human-authored, verified against approved brand guidelines (`docs/02-brand/`). Contains zero unverified claims or fake client quotes (`BR-GDL-003`).
2. **AI-Generated Preliminary Content**: Clearly flagged with the visual badge `[✦ AI-Generated Preliminary Draft]` in the discovery flow. Communicates that synthesis is algorithmic and subject to human architect validation.
3. **Human-Endorsed Architectural Content**: Content produced after a senior architect reviews a diagnostic brief, marked with the verified badge `[🛡️ Architect-Verified]`.

---

## 4. Reusable Modular Content Blocks

To guarantee DRY (Don't Repeat Yourself) templating in Jinja2, the website defines 6 standardized reusable content components:
1. **`problem_prompt_box`**: The natural language problem input with prompt chips and primary CTA.
2. **`capability_pillar_card`**: Standardized card displaying pillar icon, title, capabilities, and discovery link.
3. **`north_star_flow`**: Visual horizontal sequence displaying Understand $\rightarrow$ Translate $\rightarrow$ Build $\rightarrow$ Automate $\rightarrow$ Scale.
4. **`trust_security_callout`**: Verified statement regarding zero-training enterprise APIs and PII protection (`BD-014`).
5. **`estimation_disclaimer_block`**: The mandatory legal disclaimer accompanying all budget/timeline numbers (`BD-006`).
6. **`human_review_banner`**: The handoff callout explaining the role of senior architects (`BD-010`).
