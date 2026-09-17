# Website UX Wireframe Specifications (Low-Fidelity Blueprints)

**Document ID:** `DOC-WEB-007`  
**Classification:** Website Architecture / Phase 3 Wireframe Specifications  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-011](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-011), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [Page Specifications](file:///d:/Project_website/docs/04-website/04-PAGE-SPECIFICATIONS.md) | [AI Discovery UX Flow](file:///d:/Project_website/docs/04-website/06-AI-DISCOVERY-UX-FLOW.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Wireframe Architectural Standard

These low-fidelity wireframe blueprints define the structural anatomy, layout grids, visual hierarchy, and interaction anchors for every critical surface of `[STUDIO_NAME]`. They serve as the binding contract for frontend templating without specifying CSS implementation or arbitrary hex color codes.

---

## 2. Wireframe 01: Homepage (Desktop Viewport — 1280px Grid)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [LOGO: [STUDIO_NAME]]         What We Build ▾   How We Work   About   Contact  [CTA]   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│                                      SECTION 1: HERO                                   │
│                                                                                        │
│               Have a business problem? Let's turn it into technology.                  │
│                                                                                        │
│   We build custom software, deploy applied AI, automate workflows, and integrate       │
│   fragmented systems for startups, SMEs, and growing businesses.                       │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Describe your business problem, manual bottleneck, or technology goal...       │   │
│   │                                                                                │   │
│   │ [Prompt Chips: Manual Operations ▾ | System Integration ▾ | MVP Build ▾]       │   │
│   │                                                    [Start With Your Problem ➔] │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│   Reassurance: Free interactive diagnostic • Zero jargon required • 100% confidential  │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                               SECTION 2: PROBLEM RECOGNITION                           │
│                     Software shouldn't start with code. It starts with problems.       │
│                                                                                        │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│   │ Manual Data Entry│  │ Tool Silos & Dups│  │ Legacy Ceilings  │  │ Fragile MVPs   │ │
│   │ Copy-pasting     │  │ CRM & billing    │  │ Slow systems     │  │ Duct-taped     │ │
│   │ between tools... │  │ don't talk...    │  │ hitting volume...│  │ tech debt...   │ │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                              SECTION 3: THE TRANSLATION LAYER                          │
│                     The missing step in technology isn't code. It's translation.       │
│                                                                                        │
│       [Business Problem] ───➔ [Cognitive Translation] ───➔ [Durable Technology]        │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                               SECTION 4: WHAT WE BUILD (5 PILLARS)                     │
│                                                                                        │
│   ┌────────────────────────────────┐       ┌───────────────────────────────────────┐   │
│   │ 01. Custom Software            │       │ 02. Applied AI                        │   │
│   │ Full-stack web apps & portals  │       │ LLM extraction & document intelligence│   │
│   └────────────────────────────────┘       └───────────────────────────────────────┘   │
│   ┌────────────────────────────────┐       ┌───────────────────────────────────────┐   │
│   │ 03. Workflow Automation        │       │ 04. API & Systems Integration         │   │
│   │ Event queues & background jobs │       │ ERP, CRM & database synchronization   │   │
│   └────────────────────────────────┘       └───────────────────────────────────────┘   │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ 05. Scale & Modernization — Architecture refactoring & database performance    │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                              SECTION 5: AI DISCOVERY SPOTLIGHT                         │
│                    Explore your solution before writing a single line of code.         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Interactive Stepper Teaser: Problem ➔ Questions ➔ Map ➔ Blueprint ➔ Estimate   │   │
│   │                                                    [Start With Your Problem ➔] │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                 SECTION 6: HOW WE WORK                                 │
│        Understand ───➔ Translate ───➔ Build ───➔ Automate ───➔ Scale                   │
│             Law: "AI handles leverage. Humans handle judgement." (BD-010)              │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                              SECTION 7: CLOSING CONVERSION ANCHOR                      │
│                                Have a business problem? Start there.                   │
│                                      [Start With Your Problem ➔]                       │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ FOOTER: Pillars • Methodology • Discovery Engine • Privacy • Terms • Security (BD-014) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Wireframe 02: AI Discovery Stepper — Stage 1 & 2 (Problem & Questions)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [LOGO: [STUDIO_NAME]]                                              [Exit to Site ×]    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│ STEPPER PROGRESS: [■■■□□□□] Step 1 of 7: Business Problem (14%)                        │
│                                                                                        │
│                             What business problem are you facing?                      │
│           Describe the operational bottleneck, manual friction, or goal in your words. │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ [Textarea: e.g. We have 4 sales reps spending 3 hours a day manually entering  │   │
│   │  invoices from emails into QuickBooks, causing constant errors and delays...]  │   │
│   │                                                                                │   │
│   │ Character count: 142 chars (Recommended: 50-300 words)                         │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                        │
│   INSPIRATION CHIPS:                                                                   │
│   [Manual copy-pasting]   [Systems don't connect]   [Need an MVP fast]   [AI workflow] │
│                                                                                        │
│   Reassurance: Processed confidentially under zero-model-training enterprise terms.    │
│                                                                                        │
│   [Cancel]                                               [Analyze Business Problem ➔]  │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

                                         │
                                         ▼ (HTMX Server-Driven Transition)

┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEPPER PROGRESS: [■■■■□□□] Step 2 of 7: Operational Context (28%)                     │
│                                                                                        │
│                               A few quick questions to narrow scope                    │
│                                                                                        │
│   Q1: Which tools currently hold your primary operational data?                        │
│   ┌───────────────────────────┐  ┌───────────────────────────┐  ┌──────────────────┐   │
│   │ ( ) Spreadsheets / Excel  │  │ ( ) Custom Web App / CRM  │  │ ( ) ERP (SAP/etc)│   │
│   └───────────────────────────┘  └───────────────────────────┘  └──────────────────┘   │
│                                                                                        │
│   Q2: What is the primary operational friction slowing your team down?                 │
│   ┌───────────────────────────┐  ┌───────────────────────────┐  ┌──────────────────┐   │
│   │ ( ) Manual Data Entry     │  │ ( ) Inaccurate Reporting  │  │ ( ) System Lag   │   │
│   └───────────────────────────┘  └───────────────────────────┘  └──────────────────┘   │
│                                                                                        │
│   Q3: What is your preferred timeline to have a working solution in production?        │
│   ┌───────────────────────────┐  ┌───────────────────────────┐  ┌──────────────────┐   │
│   │ ( ) Immediate (< 4 weeks) │  │ ( ) 1 - 3 Months          │  │ ( ) Flexible     │   │
│   └───────────────────────────┘  └───────────────────────────┘  └──────────────────┘   │
│                                                                                        │
│   [◂ Back to Problem Description]                     [Generate Opportunity Map ➔]     │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Wireframe 03: AI Discovery Stepper — Stage 4 & 5 (Map & Gated Blueprint)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEPPER PROGRESS: [■■■■■□□] Step 4 of 7: Executive Opportunity Map (57%)               │
│                                                                                        │
│                               Your Executive Opportunity Map                           │
│   Based on your operational inputs, here are the highest-leverage technology vectors:  │
│                                                                                        │
│   ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐   │
│   │ [QUICK WIN: HIGH IMPACT / LOW COMP]  │  │ [CORE BUILD: HIGH IMPACT / MED COMP] │   │
│   │ Automated Webhook Sync Pipeline      │  │ Unified Operational Portal           │   │
│   │ Eliminate manual spreadsheet export  │  │ Consolidate invoice intake into      │   │
│   │ by syncing billing directly to CRM.  │  │ centralized web dashboard.           │   │
│   │ Estimated Effort: 2 - 3 Weeks        │  │ Estimated Effort: 4 - 6 Weeks        │   │
│   └──────────────────────────────────────┘  └──────────────────────────────────────┘   │
│                                                                                        │
│   ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐   │
│   │ [AUTOMATION: IMMEDIATE ROI]          │  │ [SYSTEM RISK: ATTENTION REQUIRED]    │   │
│   │ Email Invoice Document OCR Parser    │  │ QuickBooks API Rate Limit Throttling │   │
│   │ Auto-extract line items via LLM.     │  │ High transaction volume needs queue. │   │
│   └──────────────────────────────────────┘  └──────────────────────────────────────┘   │
│                                                                                        │
│   [STATUS: 100% Free & Ungated Output]                                                 │
│                                                                                        │
│   [◂ Refine Answers]            [Unlock Full Solution Blueprint & Indicative Estimate ➔]│
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘

                                         │
                                         ▼ (Click "Unlock Full Solution Blueprint")

┌────────────────────────────────────────────────────────────────────────────────────────┐
│ MODAL / PROGRESSIVE REVEAL GATE (BD-005)                                               │
│                                                                                        │
│                         Where should we send your full blueprint?                      │
│   Enter your contact details to immediately reveal the complete 18-section             │
│   architectural specification and confidence-banded indicative estimate.               │
│                                                                                        │
│   Full Name:       [ John Doe                                            ]             │
│   Corporate Email: [ john@acme-corp.com                                  ]             │
│   Company:         [ Acme Logistics (Optional)                           ]             │
│                                                                                        │
│   [✓] Send blueprint copy to my email and allow architect follow-up (BD-014).          │
│   Reassurance: No spam sequences • Zero sales harassment • Data kept confidential      │
│                                                                                        │
│   [Cancel]                                      [Unlock Complete Solution Blueprint ➔] │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Wireframe 04: AI Discovery Stepper — Stage 6 & 7 (Estimates & Handoff)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEPPER PROGRESS: [■■■■■■■] Step 6 of 7: Solution Blueprint & Indicative Estimates     │
│                                                                                        │
│   [BADGE: AI-GENERATED PRELIMINARY SPECIFICATION — PENDING ARCHITECT SIGN-OFF]         │
│                                                                                        │
│   1. Recommended Architecture Direction:                                               │
│      Modular Python FastAPI Service + Asynchronous Background Queue (Celery/Redis)     │
│      + Relational Persistence Engine + Secure Webhook Endpoints.                       │
│                                                                                        │
│   2. Indicative Budget & Timeline Planning Bands:                                      │
│   ┌───────────────────────────────────────┐  ┌─────────────────────────────────────┐   │
│   │ INDICATIVE BUDGET RANGE               │  │ INDICATIVE TIMELINE RANGE           │   │
│   │ ₹3,50,000 – ₹5,50,000  (or $4.5k-$7k) │  │ 6 – 9 Weeks to Production Delivery │   │
│   │ Confidence Rating: MEDIUM (80%)       │  │ Sprints: 3 Sprints (2 weeks each)   │   │
│   └───────────────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                                        │
│   MANDATORY DISCLAIMER (BD-006):                                                       │
│   This estimate is an automated indicative planning range to help you evaluate         │
│   project viability. It is NOT a binding commercial quote. Final scope, architecture,  │
│   and formal SOW require review and approval by a senior human architect.             │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                           STAGE 7: HUMAN-LED NEXT STEPS (BD-010)                       │
│                                                                                        │
│   Option A: Request Senior Architect Review (Free)                                     │
│   A human architect reviews this brief, verifies API limits, and emails you an         │
│   annotated architectural assessment within 1 business day (BD-013).                   │
│   [Request Human Architect Review ➔]                                                   │
│                                                                                        │
│   Option B: Apply for Paid Discovery Sprint (BD-004)                                   │
│   1-week deep-dive architectural engagement. Fully credited toward build contract.    │
│   [Inquire About Discovery Sprint ➔]                                                   │
│                                                                                        │
│   Permanent Diagnostic Recovery Link: [https://studio.com/discovery/view?token=8f9a2]  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
