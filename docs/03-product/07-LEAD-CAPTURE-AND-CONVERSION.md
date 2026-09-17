# Lead Capture, Qualification & Conversion Architecture

**Document ID:** `DOC-PRD-007`  
**Classification:** Product Specification / Phase 2 Foundational Document  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-004](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-004), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-012](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-012), [BD-013](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-013), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014)  
**Parent Framework:** [Business Model](file:///d:/Project_website/docs/01-business/BUSINESS_MODEL.md) | [Client Journey](file:///d:/Project_website/docs/01-business/CLIENT_JOURNEY.md)  
**Version:** 1.0.0 (Owner Approved Baseline)  
**Status:** Canonical Product Specification

---

## 1. Executive Summary & Strategy

The conversion engine of `[STUDIO_NAME]` is built upon a **value-first, friction-minimized philosophy** (`BD-005`).

We reject the aggressive, predatory lead capture tactics common in legacy sales funnels—such as mandatory upfront account creation, forced phone number gating, intrusive sales popups, and high-pressure telemarketing.

Instead, we provide immediate, high-value diagnostic insight anonymously, creating natural reciprocal desire for the prospective client to share their corporate credentials to unlock deeper architectural specifications and human architect review.

---

## 2. The Progressive Lead Capture Architecture (`BD-005`)

The conversion funnel transitions through three progressive friction tiers:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE THREE-TIER PROGRESSIVE CAPTURE FUNNEL                       │
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│ Tier 1: Anonymous │ 100% ungated diagnostic intake. User describes problem and answers │
│ Diagnostic        │ 4 adaptive questions. Views real-time Opportunity Map.             │
│                   │ ZERO contact info collected. Anonymous UUID session cookie.        │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Tier 2: Value-    │ User provides Work Email to unlock the full Technical Solution     │
│ Gated Blueprint   │ Blueprint, architecture diagrams, and indicative budget ranges.    │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ Tier 3: Human Gate│ User requests Principal Architect Review or Discovery Sprint       │
│ & Proposal Request│ consultation. Submits optional phone/WhatsApp for direct dialogue. │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```

---

## 3. Contact Capture Form Specification (Tier 2 Unlock)

When the user requests access to the detailed Solution Blueprint, an elegant inline card or modal appears with minimal, respectful form fields:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          TIER 2 CONTACT CAPTURE MODAL                            │
├──────────────────────────────────────────────────────────────────────────────────┤
│ HEADER: Unlock Your Technical Solution Blueprint & Indicative Estimates          │
│ SUB-HEADER: Enter your work details to access the complete component architecture│
│             and indicative investment bands.                                     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ [ Work Email Address * ]        ──► Primary identifier (corporate domains preferred)
│ [ Full Name * ]                 ──► Personal address for communication           │
│ [ Company / Project Name * ]    ──► Contextual domain anchor                     │
│ [ WhatsApp / Phone (Optional) ] ──► For urgent scheduling or mobile updates      │
├──────────────────────────────────────────────────────────────────────────────────┤
│ [x] I consent to [STUDIO_NAME] processing my project information to generate     │
│     architectural blueprints. No spam, ever. Unsubscribe with 1 click.           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ [ UNLOCK COMPLETE BLUEPRINT  → ]                                                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Data Minimization & Privacy Rules (`BD-014`)
* **No Unnecessary Friction**: We do not ask for physical mailing addresses, credit card details, company registration numbers, or annual revenue in the web form.
* **Corporate Domain Detection**: The backend flags generic domains (`gmail.com`, `yahoo.com`) as personal leads while prioritizing corporate domain leads (`acme-logistics.com`) for faster architect triage.
* **Strict Privacy Compliance**: Captured emails are stored in our local database with cryptographic timestamps and explicit consent flags adhering to global data privacy best practices.

---

## 4. Algorithmic Lead Qualification Heuristics

Upon submission, the FastAPI backend evaluates the combined diagnostic context to assign an internal triage classification:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          INTERNAL LEAD QUALIFICATION TIERS                       │
├──────────────┬───────────────────────────────────────────┬───────────────────────┤
│ Lead Tier    │ Characteristic Profile                    │ Internal SLA Target   │
├──────────────┼───────────────────────────────────────────┼───────────────────────┤
│ TIER 1: High-│ Corporate email, verified operational     │ Rapid human triage;   │
│ Intent / Fit │ bottleneck, timeline < 3 months, mature.  │ Architect review <24h │
├──────────────┼───────────────────────────────────────────┼───────────────────────┤
│ TIER 2: Early│ Startup founder, pre-code idea, seeking   │ Standard diagnostic   │
│ Stage Explore│ initial MVP architecture and budget bands.│ follow-up within 48h  │
├──────────────┼───────────────────────────────────────────┼───────────────────────┤
│ TIER 3: Non- │ Commodity clone hunter, budget mismatch,  │ Automated email with  │
│ Fit / Passive│ unethical business category (Anti-Persona)│ polite disqualification│
└──────────────┴───────────────────────────────────────────┴───────────────────────┘
```

* **Important Note**: Qualification tiers are internal routing signals only. They are never displayed to the user.

---

## 5. The Human Architect Handoff Protocol (`BD-010`, `BD-013`)

When a Tier 1 or Tier 2 prospect completes the diagnostic and clicks **"Request Principal Architect Review"**, the system executes an automated handoff pipeline:

```text
WEB APPLICATION (FastAPI Backend)                      STUDIO OPERATIONS DESK
────────────────────────────────                      ──────────────────────
1. Generates Structured Lead Dossier (JSON).    ──►   1. Instant alert dispatched to 
2. Assembles raw prompt, tags, blueprint,                 internal email & operations channel.
   and indicative complexity bands.             ──►   2. Principal Architect reviews dossier.
3. Dispatches transactional receipt to client.  ──►   3. Architect verifies feasibility, stack & SOW.
                                                ──►   4. Tailored proposal issued within 24h target (BD-013).
```

* **The Lead Dossier Contents**:
  - Raw client problem statement and industry classification.
  - User's answers across the 4 adaptive diagnostic steps.
  - Generated Opportunity Map bottlenecks and proposed architectural components.
  - Indicative planning investment and timeline bands.
  - Identified technical risks, third-party API dependencies, and open unknowns.

---

## 6. The Paid Discovery Sprint Transition (`BD-004`)

For qualified, high-intent engagements involving complex enterprise workflows, multi-system integrations, or extensive legacy data migrations, the primary conversion outcome of the diagnostic is the **Paid Discovery Sprint**:

```text
Free AI Diagnostic ──► Executive Map ──► Blueprint ──► Paid Discovery Sprint ──► Phase 1 Build
```

### Governance on Discovery Sprint Commercial Terms:
* **Approved Strategic Model**: The two-tier model of **Free AI Diagnostic $\rightarrow$ Paid Discovery Sprint** is an approved business decision (`BD-004`).
* **Packaging, Pricing & Duration**:
  > **STATUS: TBD / HYPOTHESIS — VALIDATION REQUIRED**  
  > In strict adherence to project owner decisions and the Phase 1 assumption audit, the **exact pricing**, **calendar duration** (e.g. 1 week), **commercial packaging**, and **build crediting terms** remain unfinalized hypotheses. They will be calibrated through direct customer validation and pricing sensitivity research before commercial finalization.

---

## 7. Traceability Matrix

| Requirement ID | Lead Capture Dimension | Section Reference | Decision Reference |
| :--- | :--- | :--- | :--- |
| `PRD-CAP-001` | Three-tier progressive lead capture funnel | Section 2 | `BD-005` |
| `PRD-CAP-002` | Value-first ungated Tier 1 diagnostic display | Section 2 | `BD-005` |
| `PRD-CAP-003` | Tier 2 minimal contact capture form specification | Section 3 | `BD-005`, `BD-014` |
| `PRD-CAP-004` | Data minimization & consent privacy compliance | Section 3.1 | `BD-014` |
| `PRD-CAP-005` | Algorithmic internal lead qualification triage | Section 4 | `BD-002`, `BD-007` |
| `PRD-CAP-006` | Automated Principal Architect handoff dossier | Section 5 | `BD-010`, `BD-013` |
| `PRD-CAP-007` | Paid Discovery Sprint commercial transition governance| Section 6 | `BD-004` |
