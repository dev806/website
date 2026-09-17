# Website MVP Scope & Feature Prioritization Matrix

**Document ID:** `DOC-WEB-016`  
**Classification:** Website Architecture / Phase 3 MVP Boundary Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [MVP Scope Recommendation](file:///d:/Project_website/docs/00-project/MVP_SCOPE_RECOMMENDATION.md) | [Product MVP Scope](file:///d:/Project_website/docs/03-product/08-MVP-SCOPE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. MVP Scoping Philosophy: Ruthless Focus on Value

The website MVP of `[STUDIO_NAME]` is engineered according to a strict governing law: **build only what directly validates positioning, delivers reciprocal diagnostic value, and drives qualified inbound conversations**.

We reject "resume-driven development", superficial UI bloat, and extraneous third-party tooling that creates maintenance liabilities.

---

## 2. Feature Prioritization Matrix (MoSCoW Classification)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              WEBSITE FEATURE SCOPE BOUNDARIES                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ MUST HAVE (MVP)                                                                        │
│ • Canonical Homepage (9 sections)                                                      │
│ • 5 Service Pillar Overview Pages (/services/*)                                        │
│ • Solutions Index (/solutions) & Methodology (/how-we-work)                            │
│ • About Page (/about) & Direct Contact Advisory (/contact)                             │
│ • AI Project Discovery 7-Stage Guided Stepper (/discovery)                             │
│ • Value-First Progressive Lead Gating & Email Unlock (BD-005)                          │
│ • Indicative Budget & Timeline Bands with Mandatory Disclaimers (BD-006)               │
│ • Mobile Responsive Layout (320px–1440px+) with Persistent CTA                         │
│ • Semantic WCAG 2.1 AA Accessibility & Keyboard Navigation                             │
│ • Privacy, Terms, and Security Specifications (BD-014)                                 │
│ • Anonymous-First Client Analytics Telemetry (Zero PII)                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ SHOULD HAVE (MVP IF LOW COMPLEXITY)                                                    │
│ • Session Draft Recovery via LocalStorage & URL Token (BD-015)                         │
│ • Dynamic Clarification Question Branching (3–5 questions)                             │
│ • Copyable Diagnostic Summary Link for Founders                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2 HORIZON (DEFERRED)                                                             │
│ • Downloadable PDF Solution Architecture Brief                                         │
│ • Dedicated Case Studies Directory (/case-studies) (Requires real client proof)        │
│ • Paid Discovery Sprint Booking Gateway (/discovery/book) (BD-004)                     │
│ • Multi-Currency INR/USD Dynamic Toggle (BD-003)                                       │
│ • Internal Architect Triage Pipeline Dashboard                                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ FUTURE HORIZON (LONG-TERM)                                                             │
│ • Client Collaboration Portal & Dashboard (/portal) (BD-008)                           │
│ • Dedicated Careers / Hiring Portal (/careers)                                         │
│ • Self-Serve Payment Checkout Gateway                                                  │
│ • Automated Code Boilerplate Scaffolding Engine                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ NOT JUSTIFIED / STRICTLY EXCLUDED                                                      │
│ ✗ Headless CMS (Strapi/Sanity/Contentful) — Adds bloat, cost, and build friction      │
│ ✗ Generic Floating AI Chatbot — High friction, hallucinatory, unfocused               │
│ ✗ Open-Ended Blog Mill — Avoids unmaintained low-quality content at launch             │
│ ✗ Heavyweight 3D WebGL / Canvas Animations — Slows performance, drains battery        │
│ ✗ React / Next.js SPA Frameworks — Strictly violates Python-First constraint (BD-015)  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Deep Architectural Justifications for Scope Exclusions

### A. Rejection of Headless CMS
* **Evaluation**: Evaluated Strapi, Sanity, and Contentful for marketing page editing.
* **Verdict**: **STRICTLY REJECTED FOR MVP**.
* **Reasoning**: The studio's core MVP content is highly structured and changes infrequently. Managing content directly in version-controlled Python data models and Jinja2 templates (`BD-015`) incurs **₹0 infrastructure cost**, eliminates external API points of failure, and keeps the repository 100% self-contained.

### B. Deferral of Dedicated Case Studies Directory
* **Evaluation**: Evaluated creating `/case-studies` at launch.
* **Verdict**: **DEFERRED TO PHASE 2**.
* **Reasoning**: In strict compliance with claim governance (`BR-GDL-003`), the studio will never publish fabricated client logos, fake quotes, or imaginary performance metrics. Dedicated case study teardowns will be introduced in Phase 2 once initial client deliveries yield validated, authorized outcomes.

### C. Rejection of Open-Ended Floating AI Chatbot
* **Evaluation**: Evaluated adding an intercom-style AI chat bubble in the bottom corner.
* **Verdict**: **NOT JUSTIFIED / REJECTED**.
* **Reasoning**: Generic chatbots encourage unstructured "blank box" chit-chat, increase API token costs without qualifying intent, and risk producing unpredictable responses. The structured 7-stage guided stepper (`/discovery`) is vastly superior for capturing disciplined business requirements.

### D. Deferral of Client Portal & Payment Checkouts
* **Evaluation**: Evaluated adding authenticated client accounts and Stripe/Razorpay self-serve checkout for Discovery Sprints.
* **Verdict**: **DEFERRED TO PHASE 2 / FUTURE**.
* **Reasoning**: Early enterprise and SME sales require human relationship building, tailored contract terms, and formal invoice billing. Building complex portal authentication and checkout gateways before validating product-market fit introduces unnecessary technical debt.

---

## 4. Definition of Done (DoD) for Website MVP

The website MVP is formally considered **complete and ready for public launch** only when:
1. All 12 canonical MVP routes render clean, valid HTML via FastAPI and Jinja2 with zero template errors.
2. The 7-stage AI Discovery Stepper successfully executes problem intake, maps opportunities, captures contact details, and displays indicative estimate ranges.
3. Every automated estimate prominently displays the mandatory non-binding legal disclaimer (`BD-006`).
4. All pages achieve 100% WCAG 2.1 AA keyboard navigability, semantic landmark compliance, and valid focus states.
5. All interactive elements provide touch targets $\ge 48\text{px} \times 48\text{px}$ on mobile viewports.
6. Zero fabricated claims, fake metrics, unverified certifications, or placeholder names appear anywhere in public copy.
7. Local development runs cleanly at **₹0 infrastructure cost** on Python 3.12+, FastAPI, and Microsoft SQL Server (`BD-015`).
