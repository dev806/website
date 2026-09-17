# API Contracts & Interface Schemas (JSON & Form Endpoints)

**Document ID:** `DOC-ARCH-009`  
**Classification:** System Architecture / Phase 4 Interface Contracts  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [API Architecture](file:///d:/Project_website/docs/05-architecture/08-API-ARCHITECTURE.md) | [AI Discovery Product Spec](file:///d:/Project_website/docs/03-product/03-AI-DISCOVERY-PRODUCT-SPEC.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Specification Protocol

These API contracts define the formal data transfer objects (DTOs), request bodies, response envelopes, error modes, and authentication requirements for the core AI Discovery engine of `[STUDIO_NAME]`.

---

## 2. Discovery Endpoint Specifications

---

### Endpoint 01: Initialize Discovery Session
* **Method & Route**: `POST /api/v1/discovery/start`
* **Purpose**: Initializes a new diagnostic session, sets an anonymous HTTP-only cookie, and creates the root record in SQL Server.
* **Authentication**: None (Anonymous entry).
* **Rate Limit**: 30 requests / minute / IP.
* **Request Payload**:
  ```json
  {
    "entry_point": "homepage_hero",
    "preseed_topic": null
  }
  ```
* **Success Response (`201 Created`)**:
  ```json
  {
    "success": true,
    "data": {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "stage": "START",
      "is_unlocked": false,
      "created_at": "2026-09-07T14:40:00Z"
    }
  }
  ```

---

### Endpoint 02: Submit Natural Language Problem
* **Method & Route**: `POST /api/v1/discovery/problem`
* **Purpose**: Receives client problem text, executes PII scrubbing, invokes AI classification, and transitions state machine to `PROBLEM_CAPTURED`.
* **Authentication**: Valid session cookie required.
* **Rate Limit**: 5 requests / minute / IP.
* **Request Payload**:
  ```json
  {
    "raw_text": "Our logistics operations team spends 4 hours every morning copy-pasting carrier shipping manifests from incoming emails into our QuickBooks and legacy ERP system, resulting in frequent data entry errors and dispatch delays."
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "success": true,
    "data": {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "stage": "QUESTIONS_GENERATED",
      "character_count": 256,
      "questions": [
        {
          "question_id": "q1",
          "prompt": "Which tools currently hold your primary operational shipment data?",
          "type": "single_choice",
          "options": ["QuickBooks & Legacy ERP", "Spreadsheets only", "Custom Web Portal", "Other"]
        },
        {
          "question_id": "q2",
          "prompt": "What is the typical daily volume of carrier manifests processed?",
          "type": "single_choice",
          "options": ["< 20 per day", "20 – 100 per day", "> 100 per day"]
        }
      ]
    }
  }
  ```
* **Error Scenarios**: `422 Unprocessable Entity` if `len(raw_text) < 20`.

---

### Endpoint 03: Submit Clarification Answers
* **Method & Route**: `POST /api/v1/discovery/answers`
* **Purpose**: Submits selected answers, synthesizes structured problem understanding and Opportunity Map nodes, advancing state to `OPPORTUNITY_MAP_GENERATED`.
* **Authentication**: Valid session cookie required.
* **Rate Limit**: 10 requests / minute / IP.
* **Request Payload**:
  ```json
  {
    "answers": {
      "q1": "QuickBooks & Legacy ERP",
      "q2": "20 – 100 per day"
    }
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "success": true,
    "data": {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "stage": "OPPORTUNITY_MAP_GENERATED",
      "structured_context": {
        "core_challenge": "Manual email manifest extraction and cross-system data synchronization.",
        "complexity_tier": "MEDIUM",
        "flagged_unknowns": ["Legacy ERP API availability and rate limits"]
      },
      "opportunities_count": 4
    }
  }
  ```

---

### Endpoint 04: Retrieve Executive Opportunity Map (100% Free / Ungated)
* **Method & Route**: `GET /api/v1/discovery/opportunity-map`
* **Purpose**: Returns the generated opportunity cards for Stage 4 visualization (`BD-005`).
* **Authentication**: Valid session cookie required.
* **Success Response (`200 OK`)**:
  ```json
  {
    "success": true,
    "data": {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "opportunities": [
        {
          "id": "opp-001",
          "category": "QUICK_WIN",
          "title": "Automated Email Webhook Ingestion Pipeline",
          "description": "Parse incoming carrier emails and extract structured attachment data directly into a staging queue.",
          "impact": "HIGH",
          "complexity": "LOW",
          "estimated_effort": "2 – 3 Weeks"
        },
        {
          "id": "opp-002",
          "category": "INTEGRATION",
          "title": "QuickBooks & Legacy ERP Bidirectional Sync",
          "description": "Connect staging queue directly to ERP via authenticated REST/ODBC bridge.",
          "impact": "HIGH",
          "complexity": "MEDIUM",
          "estimated_effort": "3 – 5 Weeks"
        }
      ]
    }
  }
  ```

---

### Endpoint 05: Progressive Lead Capture & Blueprint Unlock (`BD-005`)
* **Method & Route**: `POST /api/v1/discovery/lead-unlock`
* **Purpose**: Captures corporate email and name, records legal consent, elevates session status to unlocked, and triggers full Solution Blueprint synthesis.
* **Authentication**: Valid session cookie required.
* **Rate Limit**: 10 requests / hour / IP.
* **Request Payload**:
  ```json
  {
    "full_name": "Sarah Jenkins",
    "corporate_email": "sarah@acme-logistics.com",
    "company_name": "Acme Logistics Global",
    "consent_given": true
  }
  ```
* **Success Response (`200 OK`)**:
  ```json
  {
    "success": true,
    "data": {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "is_unlocked": true,
      "lead_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "message": "Solution Blueprint unlocked successfully."
    }
  }
  ```

---

### Endpoint 06: Retrieve Solution Blueprint & Indicative Estimates (`BD-006`)
* **Method & Route**: `GET /api/v1/discovery/blueprint`
* **Purpose**: Returns the full 18-section architectural blueprint and confidence-banded planning estimate.
* **Authentication**: Session must be unlocked (`is_unlocked == true`).
* **Success Response (`200 OK`)**:
  ```json
  {
    "success": true,
    "data": {
      "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status_badge": "AI_GENERATED_PRELIMINARY_DRAFT",
      "recommended_stack": "Python / FastAPI / Async Celery Queue / SQL Server",
      "sections": [
        {
          "index": 1,
          "title": "Executive Summary",
          "content": "Automated ingestion pipeline eliminating 4 daily hours of manual data entry..."
        }
      ],
      "estimate": {
        "budget_range_inr": "₹3,50,000 – ₹5,50,000",
        "budget_range_usd": "$4,200 – $6,500",
        "timeline_weeks": "6 – 9 Weeks",
        "confidence": "MEDIUM",
        "mandatory_disclaimer": "IMPORTANT NOTICE: This estimate is an automated indicative planning range..."
      }
    }
  }
  ```
* **Error Scenarios**: `403 Forbidden` if session is not yet unlocked.

---

### Endpoint 07: Request Human Architect Review (`BD-010`)
* **Method & Route**: `POST /api/v1/discovery/review`
* **Purpose**: Submits the completed diagnostic to the senior architect triage queue.
* **Authentication**: Session must be unlocked.
* **Request Payload**:
  ```json
  {
    "notes": "We would like to discuss whether our on-premise ERP firewall will allow webhooks."
  }
  ```
* **Success Response (`201 Created`)**:
  ```json
  {
    "success": true,
    "data": {
      "review_request_id": "c7a8b9c0-d1e2-3f4a-5b6c-7d8e9f0a1b2c",
      "status": "PENDING",
      "expected_triage_within": "1 business day"
    }
  }
  ```
