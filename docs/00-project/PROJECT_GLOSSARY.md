# PROJECT GLOSSARY & UNIFIED TERMINOLOGY
**Canonical Lexicon of Domain Entities, Technical Terms, and Acronyms**

---
Document Owner: Principal Project Architect & Systems Planner  
Status: PROPOSED  
Version: 1.0.0  
Last Updated: 2026-09-07  
Dependencies: [PROJECT_OVERVIEW.md](file:///d:/Project_website/docs/00-project/PROJECT_OVERVIEW.md)  
Related Documents: [DOCUMENTATION_ARCHITECTURE.md](file:///d:/Project_website/docs/00-project/DOCUMENTATION_ARCHITECTURE.md), [REQUIREMENTS_REGISTER.md](file:///d:/Project_website/docs/00-project/REQUIREMENTS_REGISTER.md)  
Decision Status: UNDER_REVIEW  
---

## 1. Executive Purpose

Semantic drift—where different team members, documents, or AI agents use the same term to mean different things—is a primary source of architectural bugs and scope creep. This glossary establishes the immutable definitions for all domain entities, business concepts, technical systems, and acronyms used across the company.

---

## 2. Business & Studio Terminology

| Term | Canonical Definition |
| :--- | :--- |
| **Technology Studio** | A hybrid organization combining high-velocity bespoke engineering services with internal IP productization, evolving from agency client work into proprietary SaaS assets. |
| **Premium Technology Partner** | The market positioning of the company; signifies deep business problem translation, high-caliber engineering, consultative architecture, and long-term partnership rather than commodity outsourced programming. |
| **ICP (Ideal Customer Profile)** | The defined target organizations (Startups, SMEs, and Growing Enterprises) possessing specific revenue thresholds, operational complexity, and high willingness to invest in technology leverage. |
| **Problem-to-Tech Translation** | The core proprietary methodology of mapping unstructured operational bottlenecks, manual human friction, and commercial objectives into technical architectures and software deliverables. |
| **Discovery Sprint** | A time-boxed, 1-to-2 week paid consultative diagnostic engagement where a Principal Architect and AI diagnostic tools analyze a client's workflows, producing an exhaustive Solution Blueprint and fixed-price build proposal. |
| **Capability Pillars** | The 5 core operational domains offered by the studio: **BUILD**, **AI**, **AUTOMATE**, **INTEGRATE**, **SCALE**. |

---

## 3. Signature Website & Discovery Terminology

| Term | Canonical Definition |
| :--- | :--- |
| **AI Project Discovery** | The interactive, multi-stage diagnostic web application that guides prospective clients through unstructured business problem extraction, qualification, and architectural translation. |
| **Project Discovery Brief** | A structured document generated during the discovery session summarizing the client's business context, identified problem, desired outcomes, constraints, budget, and timeline. |
| **Opportunity Map** | A visual and analytical matrix highlighting operational bottlenecks, high-ROI automation targets, AI leverage points, and integration opportunities discovered during the session. |
| **Solution Blueprint** | A preliminary architectural schematic recommending specific software modules, capability pillars, data flow diagrams, technical stacks, and risk mitigations tailored to the client's problem. |
| **Indicative Estimation** | An algorithmically calculated timeline (in weeks) and budgetary band (with confidence intervals) based on historical engineering complexity scores, subject to human review. |
| **Human-in-the-Loop (HITL) Gate** | The mandatory operational boundary where an AI-generated Solution Blueprint and Indicative Estimation are inspected, validated, and signed off by a licensed Principal Architect before being presented as a formal commercial proposal. |
| **Commercial Proposal** | A binding Statement of Work (SOW) detailing verified deliverables, architectural milestones, delivery timelines, payment schedules, and SLAs. |

---

## 4. Technical & Engineering Terminology

| Term | Canonical Definition |
| :--- | :--- |
| **App Router** | Next.js 15 routing architecture leveraging React Server Components (RSC) for streaming, server-side data fetching, and optimized client bundles. |
| **RSC (React Server Components)** | React components rendered purely on the server that emit zero JavaScript to the browser client bundle, drastically reducing initial load times. |
| **Edge Runtime** | A lightweight, low-latency execution environment deployed globally across CDN points of presence, ideal for streaming LLM responses and geo-routing. |
| **SSE (Server-Sent Events)** | A unidirectional HTTP protocol allowing the server to stream real-time tokens and state transitions to the web client during AI discovery synthesis. |
| **Drizzle ORM** | A lightweight, type-safe TypeScript Object-Relational Mapper that mirrors native SQL schemas with zero overhead and instantaneous edge cold-starts. |
| **pgvector** | An open-source vector similarity search extension for PostgreSQL, used to store and query high-dimensional embeddings directly within the primary database. |
| **Structured Outputs** | Technique where LLM responses are constrained to strictly conform to typed JSON schemas (via Zod or JSON Schema) with 100% syntactic determinism. |
| **Prompt Injection** | A security exploit where malicious user inputs manipulate an LLM's system prompt instructions, circumventing safety guardrails or extracting confidential system data. |
| **STRIDE** | Security threat modeling framework evaluating **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, and **E**levation of privilege. |

---

## 5. Acronyms & Traceability Identifiers

| Acronym | Expansion & Meaning |
| :--- | :--- |
| **BR** | Business Requirement (Traceability prefix, e.g. `BR-001`) |
| **PR** | Product Requirement (Traceability prefix, e.g. `PR-001`) |
| **UX** | User Experience Requirement (Traceability prefix, e.g. `UX-001`) |
| **FR** | Functional Requirement (Traceability prefix, e.g. `FR-001`) |
| **NFR** | Non-Functional Requirement (Traceability prefix, e.g. `NFR-001`) |
| **AI** | Artificial Intelligence Requirement (Traceability prefix, e.g. `AI-001`) |
| **`SEC`** | Security Requirement (Traceability prefix, e.g. `SEC-001`) |
| **`QA`** | Quality Assurance Test Case (Traceability prefix, e.g. `QA-001`) |
| **`OPS`** | Operational Requirement (Traceability prefix, e.g. `OPS-001`) |
| **`DoD`** | Definition of Done (Strict qualification rubric for merging work) |
| **MVP** | Minimum Viable Product (Phase 1 launchable baseline) |
| **RAG** | Retrieval-Augmented Generation |
| **SOW** | Statement of Work (Legally binding project contract) |
| **SLA** | Service Level Agreement |
| **TTFB** | Time To First Byte (Web performance metric) |
| **LCP** | Largest Contentful Paint (Core Web Vital metric) |
| **INP** | Interaction to Next Paint (Core Web Vital metric) |
| **CLS** | Cumulative Layout Shift (Core Web Vital metric) |
