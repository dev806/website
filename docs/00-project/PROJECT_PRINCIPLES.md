# PROJECT PRINCIPLES & GOVERNING LAWS
**Foundational Engineering, Product, AI, and Architectural Commandments**

---
Document Owner: Principal Project Architect & Systems Planner  
Status: PROPOSED  
Version: 1.0.0  
Last Updated: 2026-09-07  
Dependencies: [PROJECT_OVERVIEW.md](file:///d:/Project_website/docs/00-project/PROJECT_OVERVIEW.md)  
Related Documents: [DECISION_LOG.md](file:///d:/Project_website/docs/00-project/DECISION_LOG.md), [TECHNOLOGY_DECISION_FRAMEWORK.md](file:///d:/Project_website/docs/00-project/TECHNOLOGY_DECISION_FRAMEWORK.md), [PROJECT_CONSTRAINTS.md](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md)  
Decision Status: UNDER_REVIEW  
---

## 1. The 5 Core Philosophical Axioms

### Axiom 1: Business First, Technology Second
Technology is an operational tool to generate enterprise value, compress operating costs, or accelerate revenue. We never build features or introduce architectural layers without an explicit, quantified business justification.

### Axiom 2: Understand the Problem Before Proposing the Solution
Prescription without diagnosis is malpractice. We never present tech stacks, database schemas, or software designs until the root operational bottleneck, human user journey, and commercial constraints are thoroughly understood.

### Axiom 3: AI Where It Creates Leverage, Humans Where Judgement Matters
Artificial Intelligence is not magic pixie dust. It is applied specifically where it delivers order-of-magnitude cognitive leverage (unstructured data extraction, semantic search, pattern recognition, draft synthesis). Where accountability, ethical integrity, commercial risk, and edge-case judgment reside, human principals retain total authority.

### Axiom 4: Simplicity Outweighs Cleverness
We ruthlessly eliminate speculative generality. We choose the simplest viable architecture capable of meeting current operational scale and foreseeable 12-month requirements. We reject resume-driven development, premature microservices, and unneeded infrastructure layers.

### Axiom 5: Software Should Adapt to Business, Not Business to Software
Off-the-shelf software frequently forces businesses to mutilate their operating models to fit arbitrary software opinions. Our solutions bend, integrate, and automate around the client's competitive advantages.

---

## 2. Technical & Architectural Commandments

1. **Deterministic Over Non-Deterministic by Default**:
   - Financial calculations, database writes, access control, and state transitions must be executed by deterministic, testable code.
   - LLMs are relegated to input extraction and synthesis; they never directly mutate critical business states without schema validation.
2. **Modularity and Loose Coupling**:
   - Systems are built with strict interface boundaries. Services, database adapters, and AI model providers must be swappable via dependency injection or standardized adapters.
3. **No Unnecessary Microservices**:
   - The platform begins as a well-structured modular monolith (or unified full-stack framework with edge routing). Microservices are prohibited until isolated scaling bottlenecks or team organizational splits strictly demand them.
4. **Zero-Trust Network & Data Boundary**:
   - Internal APIs, serverless functions, and third-party webhooks must validate signatures, authenticate callers, and sanitize payloads.
5. **Observability is Not an Afterthought**:
   - Every user flow, API invocation, background job, and LLM query must emit structured logs, telemetry events, and latency metrics.

---

## 3. AI-Native Operating Principles

When considering an AI capability, engineers and architects must satisfy these 9 mandatory evaluation filters:

1. **Does AI solve a real, high-friction problem?** (Or is a standard form/SQL query faster and cheaper?)
2. **Is deterministic software better?** (Calculations, dates, sorting, boolean logic must always be deterministic).
3. **Is basic rule-based automation sufficient?** (Don't use an LLM where an `if/else` or regex suffices).
4. **What is the operational cost?** (Token usage, latency overhead, inference budget per user session).
5. **What is the failure mode?** (What happens when the model hallucinates, times out, or returns malformed JSON?)
6. **What human oversight is required?** (Is there a human-in-the-loop review before client-facing commitments?)
7. **How is quality continuously evaluated?** (Deterministic regression test suites, golden datasets, LLM-as-a-judge).
8. **What data is required and is it protected?** (Strict PII redaction, zero model training on client IP).
9. **How does the system gracefully recover when AI is wrong?** (Safe fallback defaults, user override controls).

---

## 4. Security & Privacy Commandments

1. **Zero Exposure of Secrets**:
   - Never commit API keys, database credentials, or signing tokens into source control. All secrets reside in encrypted runtime environments with automated rotation.
2. **Prompt Injection Defense in Depth**:
   - Treat all unstructured text from users, webhooks, and third-party documents as untrusted input. Sanitize inputs, enforce system prompt isolation, and validate all model outputs against strict type schemas before parsing.
3. **Client Confidentiality & Zero Data Retention**:
   - Client business discovery data must never be used to train public or proprietary foundation models without explicit contractual consent.
4. **Least Privilege Authorization**:
   - Users and background workers operate with the absolute minimum database and API privileges necessary to fulfill their responsibilities.

---

## 5. Documentation & Traceability Standards

1. **Bidirectional Traceability**:
   - Every feature must trace from a Business Requirement (`BR-xxx`) to a Product Requirement (`PR-xxx`), UX Specification (`UX-xxx`), Functional Endpoint (`FR-xxx`), Non-Functional Standard (`NFR-xxx`), AI Specification (`AI-xxx`), and Verification Test (`QA-xxx`).
2. **No Silent Assumptions**:
   - If an architectural choice lacks business consensus, it must be documented in `DECISION_LOG.md` with trade-offs, options, recommendations, and marked `[DECISION REQUIRED]`.
3. **Living Documentation**:
   - Documentation is version-controlled code. When an architectural decision or schema changes, its dependent documents must be updated in the same pull request.
