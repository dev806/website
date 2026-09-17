# Unresolved Brand Decisions & Strategic Open Questions

**Document ID:** `DOC-BRD-008`  
**Classification:** Brand Strategy / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-003](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-003), [BD-007](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-007), [BD-008](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-008)  
**Parent Framework:** [Brand Foundation](file:///d:/Project_website/docs/02-brand/01-BRAND-FOUNDATION.md) | [Brand Guidelines](file:///d:/Project_website/docs/02-brand/07-BRAND-GUIDELINES.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Active Open Questions Register

---

## 1. Executive Summary & Governance Rules

In accordance with strict project governance rules:
1. No unapproved brand assumption may be converted into a confirmed decision without written Project Owner authorization.
2. The working title `[STUDIO_NAME]` remains the mandatory placeholder across all documentation and templates until legal trademark and domain availability are certified (`BD-001`).
3. Every open question is assigned a definitive classification, an impact assessment, and a resolution trigger.

---

## 2. Master Brand Open Questions Ledger

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         MASTER BRAND OPEN QUESTIONS TABLE                        │
├─────────┬───────────────────────────────┬────────────────────────┬───────────────┤
│ Item ID │ Topic                         │ Governance Status      │ Impact Layer  │
├─────────┼───────────────────────────────┼────────────────────────┼───────────────┤
│ BOQ-001 │ Official Brand Name           │ OWNER DECISION REQ.    │ Meta, Legal   │
│ BOQ-002 │ Primary Domain Acquisition    │ RESEARCH REQUIRED      │ SEO, DNS      │
│ BOQ-003 │ Trademark Clearance           │ RESEARCH REQUIRED      │ Legal IP      │
│ BOQ-004 │ Exact Visual Identity System  │ TBD / PHASE 3 UX       │ CSS Tokens    │
│ BOQ-005 │ Exact Typography Pairing      │ TBD / PHASE 3 UX       │ Web Fonts     │
│ BOQ-006 │ Exact Hex Color Palette       │ TBD / PHASE 3 UX       │ Design Tokens │
│ BOQ-007 │ Official Logo & Mark Design   │ OWNER DECISION REQ.    │ SVG Assets    │
│ BOQ-008 │ Secondary Tagline Variants    │ VALIDATION REQUIRED    │ Marketing Copy│
│ BOQ-009 │ Brand Architecture for SaaS   │ TBD / STRATEGIC HORIZON│ Product Naming│
└─────────┴───────────────────────────────┴────────────────────────┴───────────────┘
```

---

## 3. Detailed Item Analysis

---

### `BOQ-001`: Official Brand Name Finalization
* **Current State**: Parameterized as `[STUDIO_NAME]` (`BD-001`).
* **Governance Status**: `PROJECT OWNER DECISION REQUIRED`
* **Context**: A final company moniker is required prior to public launch for incorporation, contracts, copyright notices, and open-source packages.
* **Evaluation Criteria**:
  - Phonetic clarity and ease of pronunciation across both Indian and international markets.
  - Absence of trademark conflicts in Class 42 (Computer & Software Services).
  - Availability of clean `.com` or `.in` top-level domains.
  - Conveys engineering authority, systems architecture, and intelligent leverage without sounding like an ephemeral AI hype wrapper.
* **Next Steps**: Project Owner to evaluate candidate shortlist and initiate availability checks.

---

### `BOQ-002`: Primary Domain Acquisition & TLD Strategy
* **Current State**: Unfinalized (`BD-001`).
* **Governance Status**: `RESEARCH REQUIRED`
* **Context**: Must balance India-first market credibility with planned global expansion (`BD-003`).
* **Options Evaluated**:
  1. *Primary `.com` Global Domain*: Ideal for international expansion; higher acquisition cost if aftermarket purchase is required.
  2. *Dual-Domain Routing (`.in` and `.com`)*: Acquire both; route domestic traffic to `.in` and international to `.com` via Geo-IP or maintain a single global `.com`.
  3. *Modern Tech TLDs (`.dev`, `.ai`, `.studio`)*: Popular in engineering communities, but `.com` retains highest enterprise trust for non-technical SME decision-makers.
* **Next Steps**: Conduct registrar price and availability searches once candidate brand names are shortlisted.

---

### `BOQ-003`: Formal Trademark Registration & Clearance
* **Current State**: Pending brand name selection.
* **Governance Status**: `RESEARCH REQUIRED`
* **Context**: Legal protection of the studio name, wordmark, and logo in India (under the Trade Marks Act, 1999) and internationally (via the Madrid Protocol).
* **Next Steps**: Engage trademark attorney to perform comprehensive clearance searches across Nice Class 42 and Class 9 once `BOQ-001` is narrowed.

---

### `BOQ-004`: Exact Visual Identity System (Dark vs. Light Theme Baseline)
* **Current State**: Conceptual direction established in `06-VISUAL-IDENTITY-DIRECTION.md`.
* **Governance Status**: `TBD — PHASE 3 UX DESIGN`
* **Context**: Determining whether the public marketing website defaults to an **Architectural Obsidian Dark Mode** or a **Crisp Architectural Light Mode**, or provides a zero-flicker toggle.
* **Considerations**:
  - Dark mode conveys cutting-edge technical authority and futuristic polish (popular with startup founders and CTOs).
  - Light mode provides superior readability for traditional SME business owners in bright office environments.
* **Resolution Gate**: To be evaluated and prototyped during Phase 3 UX design.

---

### `BOQ-005`: Final Typography System Pairing
* **Current State**: Candidates identified (Plus Jakarta Sans, Outfit, Geist, Inter, JetBrains Mono).
* **Governance Status**: `TBD — PHASE 3 UX DESIGN`
* **Context**: Testing rendering fidelity, font file sizes (sub-50KB budget), and sub-pixel antialiasing across Windows, macOS, iOS, and Android screens.
* **Resolution Gate**: Select final 2 web font families in Phase 3 design system tokens.

---

### `BOQ-006`: Final Hex Color System & Contrast Calibration
* **Current State**: Color architecture defined conceptually (foundational neutrals, technical accent, human warmth tone, semantic status colors).
* **Governance Status**: `TBD — PHASE 3 UX DESIGN`
* **Context**: Precise HSL/Hex values must be calibrated for WCAG 2.1 AA compliance (4.5:1 minimum contrast ratio) across both light and dark variants.
* **Resolution Gate**: Define exact color tokens in `docs/05-ux-ui/DESIGN_SYSTEM.md`.

---

### `BOQ-007`: Official Logo & Monogram Design
* **Current State**: Conceptual requirement for a minimalist vector geometric mark.
* **Governance Status**: `PROJECT OWNER DECISION REQUIRED`
* **Context**: A scalable vector logo is needed for the navigation bar, favicon, social open-graph cards, and PDF proposal headers.
* **Aesthetic Direction**: A clean architectural monogram or geometric motif representing systems connection, modularity, or data flow. Avoid literal robot icons or gears.
* **Resolution Gate**: Project Owner to commission or approve vector mark designs following brand name finalization.

---

### `BOQ-008`: Secondary Tagline Variants & Regional Resonance
* **Current State**: Primary tagline is approved: *"We turn business problems into technology."* (`BD-011`).
* **Governance Status**: `VALIDATION REQUIRED`
* **Context**: Evaluating whether secondary localized taglines are needed for specific regional or vertical campaigns (e.g. *"Custom software that adapts to your business"*, *"From spreadsheet chaos to scalable software"*).
* **Validation Method**: Test click-through rates across LinkedIn thought-leadership posts and search ads during early marketing tests.

---

### `BOQ-009`: Brand Architecture for Future SaaS & Products (`BD-008`)
* **Current State**: Master-branded endorsement model proposed (`[STUDIO_NAME]` Studio $\rightarrow$ `[Product Name] by [STUDIO_NAME]`).
* **Governance Status**: `TBD — STRATEGIC HORIZON`
* **Context**: When repeatable studio solutions are spun off into standalone multi-tenant SaaS products (Months 18–36), should they carry independent product names or remain direct sub-brands?
* **Resolution Gate**: Deferred to Stage 3 of business evolution (`BD-008`).

---

## 4. Traceability Matrix

| Open Question ID | Topic Area | Classification | Parent Requirement |
| :--- | :--- | :--- | :--- |
| `BOQ-001` | Official Brand Name | `PROJECT OWNER DECISION REQUIRED` | `BD-001` |
| `BOQ-002` | Primary Domain Strategy | `RESEARCH REQUIRED` | `BD-001`, `BD-003` |
| `BOQ-003` | Trademark Clearance | `RESEARCH REQUIRED` | `BD-001`, `BD-014` |
| `BOQ-004` | Visual Identity System | `TBD — PHASE 3 UX` | `BD-007` |
| `BOQ-005` | Final Typography Pairing | `TBD — PHASE 3 UX` | `BD-007` |
| `BOQ-006` | Final Color Palette Tokens | `TBD — PHASE 3 UX` | `BD-007` |
| `BOQ-007` | Logo & Monogram Design | `PROJECT OWNER DECISION REQUIRED` | `BD-001`, `BD-007` |
| `BOQ-008` | Secondary Tagline Testing | `VALIDATION REQUIRED` | `BD-011` |
| `BOQ-009` | SaaS Brand Architecture | `TBD — STRATEGIC HORIZON` | `BD-008` |
