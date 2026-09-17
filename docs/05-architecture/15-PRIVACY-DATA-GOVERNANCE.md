# Privacy & Data Governance Architecture Specification

**Document ID:** `DOC-ARCH-015`  
**Classification:** Data Governance / Phase 4 Privacy Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014)  
**Parent Framework:** [Database Architecture](file:///d:/Project_website/docs/05-architecture/05-DATABASE-ARCHITECTURE.md) | [Security Architecture](file:///d:/Project_website/docs/05-architecture/14-SECURITY-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Privacy-by-Design Governance Mandate

In strict accordance with Owner Decision `BD-014`, `[STUDIO_NAME]` operates under a **Privacy-by-Design** doctrine. The platform treats client business problem descriptions and architectural specifications as **strictly confidential trade secrets**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 4 DATA CLASSIFICATION TIERS                           │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ DATA CLASSIFICATION   │ EXAMPLES                   │ HANDLING & ENCRYPTION CONTROLS    │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 1: Public Static │ Service pillars, homepage  │ Publicly cacheable; zero access   │
│ Marketing Data        │ copy, sitemap, legal terms.│ restrictions.                     │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 2: Confidential  │ Natural language problem   │ Scrubbed of secrets; stored in DB │
│ Business Diagnostic   │ text, operational details, │ with session token isolation;     │
│ Context               │ opportunity maps.          │ zero model training (BD-014).     │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 3: Personally    │ Lead full name, corporate  │ Encrypted in transit & at rest;   │
│ Identifiable Info     │ email address, company.    │ isolated in `dbo.leads`; excluded │
│ (PII)                 │                            │ from telemetry and AI logs.       │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 4: Anonymous     │ `discovery_started`,       │ Pseudorandom session hashes;      │
│ Funnel Telemetry      │ `opportunity_map_viewed`.  │ zero PII; policy-governed purge.  │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 2. AI Data Protection & Provider Evaluation Requirement (`BD-014`)

1. **External AI Provider Evaluation & Non-Training Requirement**: The architecture mandates that any commercial AI provider selected must be explicitly evaluated for data-use and training policies before production use, with enforceable contractual terms prohibiting the use of client operational inputs for model training or evaluation. Provider-specific contractual verification remains: `RESEARCH / TECHNICAL VALIDATION REQUIRED`.
2. **Pre-Transit PII Sanitization**: User problem text is processed through an automated regex scrubber removing credit cards, passwords, and government IDs prior to outbound network transit.
3. **Prompt Ephemerality**: Models are called statelessly. No persistent assistant threads or vendor-side conversation stores are created.

---

## 3. Data Retention Architecture: Capability vs. Policy

The architecture strictly distinguishes between the **retention mechanism** (an engineering capability) and the **exact retention duration** (a governance and policy decision):

* **Retention Mechanism (Architectural Capability)**: The database and task runner provide automated scheduled purge sweeps, soft-delete flags (`is_deleted`), and parameterized deletion queries to execute data removal reliably.
* **Exact Retention Duration (Policy Decision Required)**: Specific retention periods are NOT currently approved as final commitments. The durations below represent candidate baselines requiring formal Project Owner and legal ratification:

| Data Category | Retention Mechanism (Capability) | Candidate Baseline Duration | Policy Status |
| :--- | :--- | :--- | :--- |
| **Abandoned Anonymous Sessions** | Scheduled background sweeper deletes uncompleted anonymous session records. | Candidate: 30 Days | `POLICY DECISION REQUIRED` |
| **Unlocked Leads & Blueprints** | Retained in primary tables; deleted upon verified client request. | Candidate: Indefinite (Active Relationship) | `POLICY DECISION REQUIRED` |
| **Magic Link Tokens** | Cryptographic token expiration verified during link redemption; expired rows purged. | Candidate: 7 Days | `POLICY DECISION REQUIRED` |
| **Raw Funnel Telemetry Events** | Aggregated into summary counts; granular event logs swept. | Candidate: 90 Days | `POLICY DECISION REQUIRED` |

---

## 4. Consent Governance & Data Minimization

1. **Explicit Timestamped Consent (`dbo.lead_consents`)**: Contact details are captured only at Stage 5 (`BD-005`). The system records the exact UTC timestamp, consent version text, and hashed IP address.
2. **Strict Purpose Limitation**: Email addresses are collected solely to deliver the Solution Blueprint and facilitate human architect review. They are never added to bulk third-party advertising databases or cold marketing sequences.
3. **Data Subject Rights Support (Compliance-Ready Alignment Direction)**: The persistence layer is designed to support DPDP/GDPR alignment direction for data export and deletion without asserting premature legal certification:
   - A single parameterized query `EXEC DeleteLeadData @LeadId = ...` permanently purges or anonymizes all associated sessions, problem statements, and blueprint records upon verified client request.
