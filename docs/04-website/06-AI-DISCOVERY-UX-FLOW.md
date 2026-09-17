# AI Discovery Experience: Detailed UX & Interaction Flow

**Document ID:** `DOC-WEB-006`  
**Classification:** Website Architecture / Phase 3 Product UX Flow  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-011](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-011), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [AI Discovery Product Spec](file:///d:/Project_website/docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md) | [Opportunity Map Spec](file:///d:/Project_website/docs/03-product/04-OPPORTUNITY-MAP-SPEC.md) | [Estimation Engine Spec](file:///d:/Project_website/docs/03-product/06-ESTIMATION-ENGINE-SPEC.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Flow Overview & Architectural Journey

The **AI Project Discovery Engine** is an interactive, adaptive cognitive intake experience running directly in the browser via server-rendered HTMX and Alpine.js (`BD-015`). It guides users step-by-step from raw business frustration to a structured architectural blueprint:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE 7-STAGE AI DISCOVERY UX JOURNEY                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ENTRY] ➔ [STAGE 1] ➔ [STAGE 2] ➔ [STAGE 3] ➔ [STAGE 4] ➔ [STAGE 5] ➔ [STAGE 6] ➔ [7]│
│   Click     Natural     Dynamic     Structured   Executive   Progressive Indicative  Human │
│   "Start    Language    Context     Understand   Opportunity Blueprint   Budget &    Review│
│    Problem" Input       Questions   Review       Map         Unlock      Timeline    Bridge│
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage-by-Stage UX Specifications

---

### ENTRY TRIGGER: Launching Discovery
* **User Action**: Clicks **"Start With Your Problem"** (`BD-012`) from global nav, hero, or contextual in-page banners.
* **URL Resolution**: Navigates to `/discovery` (or opens embedded stepper modal on desktop).
* **Initial State**: Clean, focused interface with generous whitespace, a 7-step progress bar (currently at Step 1: 14%), and ambient dark mode styling.

---

### STAGE 1: Natural Language Problem Input
* **User Goal**: Articulate their current operational friction, bottleneck, or system ambition without worrying about software jargon.
* **System Responsibility**: Provide a reassuring, low-friction textarea with contextual prompt starters and real-time character guidance.
* **User Input**: Multi-line natural language text (minimum 20 characters, recommended 50–300 words).
* **Prompt Starters / Inspiration Chips**:
  - *"Our operations team spends 15 hours a week manually copy-pasting spreadsheet data into our billing tool."*
  - *"We have a working prototype, but it can't handle more than 50 concurrent users without database crashes."*
  - *"We want to automate customer onboarding and document verification using applied AI without data leaks."*
* **Expected Output**: Primary button lights up: **"Analyze Business Problem"**.
* **Progress Indication**: Stepper indicator: `Step 1 of 7 — Business Problem`.
* **Validation**: Text length $\ge 20$ chars. If empty, input border gently highlights with accessible tooltip: *"Please describe the problem in a few words to begin."*
* **Uncertainty State**: If user writes vague text (e.g. *"I want an app"*), system accepts it gracefully and uses Stage 2 questions to unpack context.
* **Back / Edit Behavior**: N/A (Initial screen).
* **Mobile Behavior**: Auto-expanding textarea; virtual keyboard opens with action button *Done*; screen avoids horizontal scroll.
* **Accessibility**: `<label for="problem-input">` properly bound; `aria-describedby` links to prompt tips.
* **Trust Messaging**: *"Your problem description is processed confidentially under zero-model-training enterprise terms (`BD-014`)."*

---

### STAGE 2: Dynamic Clarification Questions
* **User Goal**: Clarify boundary conditions, data complexity, and operational urgency through quick, high-leverage multiple-choice selections.
* **System Responsibility**: Analyze the Stage 1 problem text and render 3 to 5 highly relevant multiple-choice questions (e.g. current software tools, scale/volume, primary bottleneck, timeline expectations).
* **User Input**: Single-select radio cards or multi-select pill buttons.
* **Expected Output**: Selection indicators illuminate; active answers are dynamically batched; button **"Generate Opportunity Map"** becomes active.
* **Progress Indication**: Stepper indicator: `Step 2 of 7 — Operational Context (28%)`.
* **Validation**: At least 1 answer per question required; default option *"I'm not sure / Need advice"* always available to prevent drop-off.
* **Error State**: Non-blocking toast notification if network fails during dynamic question fetch: *"Retrying questions..."*
* **Back / Edit Behavior**: *"Back to Problem Description"* button restores Stage 1 input intact.
* **Mobile Behavior**: Large 48px touch targets for answer cards; vertical stacking.
* **Trust Messaging**: *"We ask only what's necessary to accurately size your technology options."*

---

### STAGE 3: Structured Understanding Review
* **User Goal**: Verify that `[STUDIO_NAME]`'s engine has accurately understood their business problem before synthesizing technology recommendations.
* **System Responsibility**: Present a concise, 4-point structured synthesis of the problem:
  1. *Core Operational Challenge*
  2. *Impacted Business Workflows*
  3. *Estimated Technical Complexity Band*
  4. *Identified Unknowns & Risks*
* **User Input**: Click **"Looks Accurate — Explore Opportunities"** or click **"Edit / Refine Details"**.
* **Expected Output**: Transition to Stage 4.
* **Progress Indication**: Stepper indicator: `Step 3 of 7 — Problem Synthesis (42%)`.
* **Uncertainty State**: Highlights flagged unknowns in amber badges: *"Unknown: Current database format"*.
* **Mobile Behavior**: Card-based vertical layout with clear divider rules.

---

### STAGE 4: Real-Time Executive Opportunity Map (100% Free & Ungated)
* **User Goal**: Discover actionable technology levers, automation potential, and architectural patterns addressing their problem.
* **System Responsibility**: Render the interactive **Executive Opportunity Map** across 5 categories:
  - *Immediate Quick Wins* (High Impact, Low Complexity)
  - *Strategic Core Builds* (High Impact, High Complexity)
  - *Automation Targets* (Repetitive tasks to eliminate)
  - *Integration Requirements* (Systems to connect)
  - *Architecture & Data Risks* (Fragile bottlenecks to de-risk)
* **User Input**: Interactive inspection of opportunity nodes (clicking cards reveals rationale and complexity signals).
* **Expected Output**: Visual matrix displaying opportunities ranked by impact and feasibility.
* **Progress Indication**: Stepper indicator: `Step 4 of 7 — Opportunity Map (57%)`.
* **Reciprocal Value Milestone**: **This entire stage is 100% ungated (`BD-005`)**. The visitor has received high-value strategic clarity with zero contact capture.
* **Call-to-Action**: Prominent button: **"Unlock Full Solution Blueprint & Indicative Estimates"**.
* **Trust Messaging**: *"This Opportunity Map is generated based on your inputs and approved studio architecture patterns."*

---

### STAGE 5: Solution Blueprint Reveal (Progressive Lead Gating)
* **User Goal**: Access the comprehensive 18-section architectural blueprint detailing recommended tech stack, data models, and system components.
* **System Responsibility**: Enforce value-first progressive gating (`BD-005`):
  - High-level Blueprint Executive Summary is visible.
  - Deeper components (Detailed Architecture Direction, Data Pipeline Schemas, and Indicative Budget Estimates) require contact capture.
* **User Input**:
  - *Full Name*
  - *Corporate / Work Email*
  - *Company Name* (Optional)
  - *Consent Checkbox*: *"Send blueprint copy to my email and allow architect follow-up."*
* **Expected Output**: Immediate client-side unlock via HTMX swapping; full 18-section Blueprint renders on screen.
* **Progress Indication**: Stepper indicator: `Step 5 of 7 — Solution Blueprint (71%)`.
* **Data Minimization Law**: Only 2 mandatory fields (Name & Email). Zero phone number demands, zero password creation, zero spam marketing opt-ins (`BD-014`).
* **Trust Messaging**: *"We respect your privacy. No spam. No automated marketing sequences. Used solely for blueprint delivery and architect triage."*

---

### STAGE 6: Indicative Budget & Timeline Estimation Bands
* **User Goal**: Understand realistic market cost and duration ranges to evaluate commercial viability and secure internal budget alignment.
* **System Responsibility**: Render confidence-banded indicative sizing based on input signals:
  - *Indicative Budget Range*: Low-to-High Bands (e.g. ₹X,XX,XXX – ₹X,XX,XXX / \$X,XXX – \$XX,XXX).
  - *Indicative Timeline*: Low-to-High Duration Bands (e.g. 6–10 Weeks).
  - *Confidence Rating*: Low / Medium / High based on completeness of user input.
  - *Key Cost Drivers*: Integrations, AI models, data migration complexity.
* **Mandatory Non-Binding Legal Disclaimer (`BD-006`)**:
  > **IMPORTANT NOTICE:** This estimate is an automated indicative planning range designed to help you gauge project scope. It does NOT constitute a binding commercial quote or contractual proposal. Final scope, architecture, and pricing require comprehensive review by a senior human architect.
* **Progress Indication**: Stepper indicator: `Step 6 of 7 — Indicative Estimates (85%)`.
* **Trust Messaging**: *"We believe in transparent pricing. No artificial lowball estimates; no hidden scope expansions."*

---

### STAGE 7: Human Architect Review Bridge & Handoff
* **User Goal**: Transition their self-service diagnostic output into a real-world engagement with senior technology partners.
* **System Responsibility**: Present dual human next-step pathways:
  1. **Request Senior Architect Review (Free)**: An architect reviews the blueprint, validates assumptions, and sends an annotated evaluation within 1 business day (`BD-013`).
  2. **Explore Paid Discovery Sprint (`BD-004`)**: Apply for a dedicated 1-week architectural sprint for production-ready engineering specs (`HYPOTHESIS — VALIDATION REQUIRED`).
* **User Input**: Click **"Request Human Architect Review"** or submit additional notes/RFPs.
* **Expected Output**: Dedicated confirmation screen with session token, copyable brief link, and next-step timeline expectation.
* **Progress Indication**: Stepper indicator: `Step 7 of 7 — Complete (100%)`.
* **Session Continuity**: Generates a persistent unique diagnostic recovery link (e.g. `/discovery/review?session=uuid`) emailed to the user (`BD-015`).
