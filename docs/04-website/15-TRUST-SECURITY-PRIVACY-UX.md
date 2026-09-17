# Website Trust, Security & Privacy UX Specifications

**Document ID:** `DOC-WEB-015`  
**Classification:** Website Architecture / Phase 3 Trust & Privacy Architecture  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-013](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-013), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014)  
**Parent Framework:** [Brand Guidelines](file:///d:/Project_website/docs/02-brand/07-BRAND-GUIDELINES.md) | [Product Boundaries](file:///d:/Project_website/docs/03-product/10-PRODUCT-BOUNDARIES.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Trust Architecture Mandate & Compliance Governance

In strict accordance with Owner Decision `BD-014`, `[STUDIO_NAME]` enforces a **verifiable, privacy-first, and compliance-ready posture**. 

### Governance Rule on Compliance Claims
> **MANDATORY POLICY (`BD-014`):** Marketing copy and UI micro-text must **NEVER make unverified statutory certifications** (such as *"SOC 2 Type II Certified"*, *"HIPAA Compliant"*, or *"ISO 27001 Certified"*) without formal independent legal and third-party audit verification. The website uses **compliance-ready, privacy-respecting, and security-best-practice language**.

---

## 2. User-Facing Trust & Transparency Contracts

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 5 TRUST PILLARS OF THE UI                             │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│ 1. ZERO MODEL TRAINING        │ 2. DATA MINIMIZATION          │ 3. ESTIMATION CLARITY  │
│ Enterprise zero-retention API │ Only Name & Email collected;  │ Prominent non-binding  │
│ agreements protect inputs.    │ zero forced password accounts.│ disclaimers on prices. │
├───────────────────────────────┼───────────────────────────────┼────────────────────────┤
│ 4. HUMAN ACCOUNTABILITY       │ 5. INTELLECTUAL PROPERTY      │                        │
│ Clear badging of AI draft vs. │ Clients own 100% of custom    │                        │
│ senior architect sign-off.    │ code, schemas, and assets.    │                        │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘
```

---

## 3. UI Placement of Trust Elements Across Key Surfaces

### A. AI Discovery Input Surface (`/discovery` — Stage 1)
* **Placement**: Directly beneath the natural language problem textarea.
* **Micro-Copy**:
  > 🔒 **Enterprise Confidentiality:** Your problem description is processed through secure, enterprise-grade AI endpoints governed by strict zero-model-training agreements. Your operational insights are never used to train public models.

### B. Progressive Lead Capture Gate (`/discovery` — Stage 5)
* **Placement**: Inside the email capture modal.
* **Micro-Copy**:
  > 🛡️ **No Spam Guarantee:** We respect your inbox. We do not trigger automated cold sequences, sell contact data to third parties, or badger you with unwanted sales calls. Your email is used solely to transmit your Solution Blueprint and coordinate optional architect review.

### C. Indicative Budget & Timeline Bands (`/discovery` — Stage 6)
* **Placement**: Immediately below the budget/timeline band display.
* **Mandatory Legal Disclaimer (`BD-006`)**:
  > **IMPORTANT NOTICE:** This estimate is an automated indicative planning range designed to help you gauge project scope. It does NOT constitute a binding commercial quote or contractual proposal. Final scope, architecture, and pricing require comprehensive review and sign-off by a senior human architect.

### D. Human Architect Review Bridge (`/discovery` — Stage 7)
* **Placement**: Accompanying the architect review trigger button.
* **Micro-Copy**:
  > 👤 **Human Judgement First:** AI generates our preliminary blueprints, but experienced human technology architects evaluate system viability, verify third-party API constraints, and sign off on all commercial commitments (`BD-010`).

---

## 4. Security & Data Minimization Practices

1. **Anonymous First Diagnostic**: Visitors can interact with Stages 1 through 4 of the AI Discovery engine completely anonymously. No account creation, social login, or phone number is ever demanded upfront (`BD-005`).
2. **Cookie-Free Posture**: The MVP utilizes zero marketing or third-party behavioral cookies. The only cookies utilized are secure, HTTP-only, SameSite session identifiers necessary for diagnostic state continuity.
3. **Automated PII Scrubbing**: The FastAPI backend integrates a lightweight PII sanitization filter that strips recognized credit card numbers, passwords, and government ID numbers from problem text before passing data to LLM synthesis.
4. **Data Retention Transparency**: Unclaimed diagnostic drafts are purged automatically after 30 days. Leads who request human review have their diagnostic sessions archived securely in the database with strict role-based access control.
5. **Clear Legal Access**: Every page footer maintains direct, unblocked links to `/privacy`, `/terms`, and `/security`, ensuring full transparency for legal evaluators.
