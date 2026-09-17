# Website Information Architecture & Content Topology

**Document ID:** `DOC-WEB-003`  
**Classification:** Website Architecture / Phase 3 Information Architecture  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-002](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-002), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-011](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-011), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012)  
**Parent Framework:** [Website Strategy](file:///d:/Project_website/docs/04-website/01-WEBSITE-STRATEGY.md) | [Sitemap](file:///d:/Project_website/docs/04-website/02-SITEMAP.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Information Architecture Principles

The information architecture of `[STUDIO_NAME]` is built upon a fundamental cognitive truth: **business leaders do not browse websites looking for software libraries or database engines; they search for relief from operational friction and confidence in a technology partner**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CORE CONTENT HIERARCHY OF EVERY PAGE                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   1. RECOGNIZE THE BUSINESS PROBLEM                                                    │
│      Acknowledge operational bottlenecks, manual pain, or growth ceilings.             │
│                                  │                                                     │
│                                  ▼                                                     │
│   2. TRANSLATE INTO VALUE & CAPABILITY                                                 │
│      Frame technology as an adaptable business asset, not a complex jargon dump.       │
│                                  │                                                     │
│                                  ▼                                                     │
│   3. DEMONSTRATE ARCHITECTURAL RIGOR                                                   │
│      Show clear systems blueprints, automation workflows, and integration patterns.    │
│                                  │                                                     │
│                                  ▼                                                     │
│   4. GROUND WITH HUMAN JUDGEMENT                                                       │
│      Reassure the buyer with human-in-the-loop oversight, privacy, and accountability. │
│                                  │                                                     │
│                                  ▼                                                     │
│   5. ACTIONABLE NEXT STEP                                                              │
│      Primary CTA: "Start With Your Problem" (/discovery)                               │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Navigation Architecture & Menu Systems

```
                              ┌─────────────────────────┐
                              │     GLOBAL HEADER       │
                              └────────────┬────────────┘
                 ┌─────────────────────────┼─────────────────────────┐
                 │                         │                         │
      ┌──────────┴──────────┐   ┌──────────┴──────────┐   ┌──────────┴──────────┐
      │     PRIMARY NAV     │   │    SECONDARY NAV    │   │    ACTION ANCHOR    │
      │ • What We Build ▾   │   │ • About             │   │ [Start With Your    │
      │ • How We Work       │   │ • Contact           │   │  Problem] (Button)  │
      └─────────────────────┘   └─────────────────────┘   └─────────────────────┘
                 │
   ┌─────────────┴─────────────┐
   │ ▾ MEGA/POPOVER CONTENT    │
   │ • Custom Software         │
   │ • AI Engineering          │
   │ • Workflow Automation     │
   │ • API & Integrations      │
   │ • Scale & Modernization   │
   │ • Solutions Blueprints    │
   └───────────────────────────┘
```

### A. Primary Desktop Navigation (Sticky, High Contrast)
1. **Brand Identity / Home Link**: Canonical logo lockup `[STUDIO_NAME]`, linking directly to `/`.
2. **What We Build (Interactive Dropdown)**:
   - *Pillars*: Software Engineering (`/services/software`), Applied AI (`/services/ai`), Automation (`/services/automation`), Integrations (`/services/integrations`), Scale (`/services/scale`).
   - *Blueprints*: Outcome-driven architectures (`/solutions`).
3. **How We Work**: Links to `/how-we-work` (explaining the 5-step North Star and Human+AI collaboration doctrine).
4. **About**: Links to `/about` (studio origins, principles, engineering standards).
5. **Contact**: Links to `/contact` (direct architect advisory).
6. **Hero Action Anchor**: High-prominence button: **"Start With Your Problem"** (`/discovery`).

### B. Mobile Navigation (Drawer + Persistent Bottom Bar)
* **Drawer Navigation**: Clean slide-over triggered by a 44px hamburger icon, containing all primary and secondary routes.
* **Persistent Bottom Conversion Bar**: Stays fixed at the bottom of the viewport on mobile screens:
  - Label: *"Have a business problem?"*
  - CTA Button: **"Start With Your Problem"** (`/discovery`).

### C. Universal Footer Architecture (4 Quadrants)
1. **Pillars & Capabilities**: Direct links to all 5 service pillar pages.
2. **Methodology & Blueprints**: Links to `/solutions`, `/how-we-work`, `/about`.
3. **Product & Conversion**: Primary link to `/discovery`, `/contact`, and direct advisory email.
4. **Governance & Legal**: `/privacy`, `/terms`, `/security`, and active copyright notice.

---

## 3. Contextual Linking & Cross-Surface Integration

No page on the website is a dead end. Every page maintains strict contextual links that propel the user forward into the **AI Project Discovery** experience:

```
┌───────────────────────────┬────────────────────────────────────────────────────────────┐
│ PAGE SURFACE              │ CONTEXTUAL IN-PAGE TRANSITION TRIGGER                      │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ Homepage                  │ • Hero Banner: "Start With Your Problem"                   │
│                           │ • Problem Translation Diagram: "Explore Your Blueprint"    │
│                           │ • Discovery Spotlight: Interactive Stepper preview card    │
│                           │ • Page Footer Anchor: "Ready to turn a problem into code?" │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ Service Pillar Pages      │ • Mid-page Banner: "Have an operational bottleneck in      │
│ (/services/*)             │   this domain? Run a free 3-minute diagnostic."            │
│                           │ • Bottom Section: Pre-populated CTA passing domain tag.    │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ Solutions Index           │ • Blueprint Cards: "Diagnose your readiness for this       │
│ (/solutions)              │   solution architecture" -> launches /discovery.          │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ How We Work               │ • Stage 1 (Understand) Breakdown: "Experience Stage 1      │
│ (/how-we-work)            │   firsthand with our AI Discovery engine."                 │
├───────────────────────────┼────────────────────────────────────────────────────────────┤
│ About the Studio          │ • Philosophy Section: "See how we think about problems     │
│ (/about)                  │   before writing code." -> /discovery.                     │
└───────────────────────────┴────────────────────────────────────────────────────────────┘
```

---

## 4. Persona User Pathways & Content Flow

### Path 1: Non-Technical Founder (Speed & Cost Sensitivity)
1. **Entry**: Lands on Homepage via organic referral or direct search.
2. **First Impression (0–5s)**: Reads headline: *"Have a business problem? Let's turn it into technology."* Observes reassurance: *"You don't need to know what technology you need."*
3. **Exploration (5–30s)**: Skims Section 2 (Problem Recognition) and identifies with *"Need an MVP fast without technical debt"*.
4. **Conversion Action**: Clicks **"Start With Your Problem"** (`/discovery`).
5. **Outcome**: Enters natural language problem, answers 3 guided questions, reviews Opportunity Map, unlocks preliminary Blueprint and indicative budget range.

### Path 2: SME Business Operator (Manual Bottleneck & Operational Friction)
1. **Entry**: Lands on `/services/automation` via targeted search query.
2. **Engagement (0–45s)**: Reads how disconnected systems and manual spreadsheets are consolidated into automated, resilient Python pipelines.
3. **Contextual Shift**: Reaches in-page discovery banner: *"Want to know which repetitive workflows can be automated first?"*
4. **Conversion Action**: Clicks embedded CTA: **"Analyze Your Workflow Bottlenecks"** (navigates to `/discovery?topic=automation`).
5. **Outcome**: Generates an Opportunity Map highlighting high-ROI automation targets.

### Path 3: Growth Executive / CTO (Modernization & Scalability)
1. **Entry**: Lands on `/` or `/how-we-work`.
2. **Evaluation (0–90s)**: Evaluates the engineering principles, Python-first architecture, human-in-the-loop governance (`BD-010`), and security standards (`BD-014`).
3. **Validation**: Reviews `/security` to verify zero-retention enterprise API commitments.
4. **Conversion Action**: Either launches `/discovery` to benchmark their system requirements or submits `/contact` for an executive-to-executive architectural dialogue.

---

## 5. Information Architecture Constraints

1. **Maximum Click Depth**: Every core piece of information and the AI Discovery tool is reachable in **$\le 2$ clicks** from any page on the site.
2. **No Orphan Pages**: Every page in the sitemap is linked from both global navigation/footer and contextual in-body references.
3. **Strict Mobile Ergonomics**: Navigation menus, dropdowns, and discovery controls are touch-friendly with minimum touch targets of **44px $\times$ 44px**.
