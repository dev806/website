# AI Subsystem Architecture & Gateway Specification

**Document ID:** `DOC-ARCH-010`  
**Classification:** AI Architecture / Phase 4 Engineering Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [AI Discovery Product Spec](file:///d:/Project_website/docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. AI Architectural Philosophy: Leverage Without Hallucination

The AI subsystem of `[STUDIO_NAME]` operates strictly under the studio's foundational law:
> **"AI handles leverage. Humans handle judgement."** (`BD-010`)

It is **NOT an autonomous agent playground** or an unconstrained chatbot. It is an **isolated cognitive acceleration gateway** executing deterministic classification, structured extraction, and template synthesis.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE AI GATEWAY ARCHITECTURE                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   Domain Service ──➔ [AI Gateway Interface]                                           │
│                             │                                                          │
│             ┌───────────────┴───────────────┐                                          │
│             ▼                               ▼                                          │
│     [Prompt Template Engine]      [PII Sanitizer & Guardrails]                         │
│             │                               │                                          │
│             └───────────────┬───────────────┘                                          │
│                             ▼                                                          │
│                 [Provider Adapter Layer] ──➔ (LiteLLM / Direct SDK)                    │
│                             │                                                          │
│                             ▼                                                          │
│            [External LLM (Zero-Retention API)]                                         │
│                             │                                                          │
│                             ▼                                                          │
│                [Pydantic v2 Schema Parser]                                             │
│                             │                                                          │
│              ┌──────────────┴──────────────┐                                           │
│              ▼                             ▼                                           │
│       [Valid Schema DTO]           [Parsing / Type Error]                              │
│              │                             │                                           │
│              ▼                             ▼                                           │
│      Returned to Domain          Auto-Retry / Fallback Heuristic                       │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Subsystems

### A. Provider Abstraction Layer (Gateway Interface)
* The gateway encapsulates all external API communications behind a single Python abstract base class (`AIGatewayInterface`).
* **Provider Independence**: Domain code never imports `openai`, `anthropic`, or `google-genai` directly. Swapping or load-balancing models requires changing only configuration variables (`AI_PRIMARY_MODEL`, `AI_FALLBACK_MODEL`).
* **Provider Selection Posture**: Provider selection remains `TECHNICAL EVALUATION REQUIRED`. During development, local mock adapters or free/tier models are utilized to preserve **₹0 development cost** (`CST-CNF-008`).

### B. Prompt Template Management
* All prompt templates reside in version-controlled Python files (`app/ai_gateway/prompts.py`).
* Prompts are treated as immutable code assets with semantic versioning (e.g. `PROMPT_PROBLEM_CLASSIFIER_V1`).
* System instructions strictly enforce:
  1. *Role Boundary*: Act as a senior systems architect decomposing business friction.
  2. *Format Rule*: Output raw JSON conforming strictly to the provided Pydantic JSON schema.
  3. *Integrity Rule*: Never fabricate statistics, client testimonials, or binding price commitments.

### C. Structured Output Extraction via Pydantic v2
* The gateway eliminates unstructured Markdown or free-form prose parsing.
* Calls use model structured output modes (JSON mode / Tool Calling / Function Calling) mapped directly to target Pydantic schemas:
  - `StructuredProblemContextDTO` (Stage 1 extraction).
  - `ClarificationQuestionsDTO` (Stage 2 question generator).
  - `OpportunityMapDTO` (Stage 4 synthesis).
  - `DraftBlueprintDTO` (Stage 5 section drafting).

---

## 3. Resilience, Retries & Fallback Engineering

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI FAULT TOLERANCE MATRIX                                 │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ FAILURE MODE          │ DETECTION CRITERIA         │ MITIGATION / FALLBACK ACTION      │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ API Timeout           │ HTTP latency > 10.0s       │ Abort request. Retry once with    │
│                       │                            │ secondary fallback model.         │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Schema Validation     │ Pydantic ValidationError   │ Feed error back to model for      │
│ Failure (Malformed)   │                            │ single self-correction retry.     │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Rate Limit Throttling │ HTTP 429 Too Many Requests │ Exponential backoff with jitter   │
│                       │                            │ (2s, 4s, 8s).                     │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Total Provider Outage │ 3 consecutive 5xx failures │ Engage Circuit Breaker: Fall back │
│                       │                            │ to deterministic keyword catalog. │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

### The Deterministic Heuristic Fallback
If external AI APIs become completely unavailable or rate-limited:
- The discovery engine seamlessly engages a **pure Python deterministic heuristic fallback engine** (`app/content/fallback_catalog.py`).
- It extracts domain keywords (e.g. *"QuickBooks"*, *"manual"*, *"database"*) from the input text and maps them directly to pre-curated studio Opportunity Maps and Blueprints.
- The user experiences zero crash or error page; the UI clearly displays: `[✦ Preliminary Blueprint generated via Studio Catalog Standards]`.

---

## 4. Temperature, Determinism & Cost Governance

1. **Hyperparameter Tuning**:
   - Classification & Question Generation: `temperature = 0.1` (Maximum determinism and consistency).
   - Blueprint Section Drafting: `temperature = 0.3` (Slight lexical variety while strictly adhering to architectural bounds).
2. **Token Budget & Telemetry**:
   - Every AI invocation logs `prompt_tokens`, `completion_tokens`, `total_tokens`, and estimated cost in milliseconds to structured application logs.
   - Per-request token limits: Maximum 1,500 input tokens / 2,000 output tokens.
3. **Data Protection & Provider Data-Use Evaluation (`BD-014`)**:
   - The architecture mandates that any commercial AI provider selected must be evaluated for data-use and training policies before production use. Enforceable contractual terms must prohibit using client operational disclosures for model training or evaluation.
   - Provider-specific contractual verification remains: `RESEARCH / TECHNICAL VALIDATION REQUIRED`.
