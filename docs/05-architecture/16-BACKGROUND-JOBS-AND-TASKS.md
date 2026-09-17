# Background Jobs & Asynchronous Tasks Architecture

**Document ID:** `DOC-ARCH-016`  
**Classification:** System Architecture / Phase 4 Task Processing  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [ADR-013](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md#adr-013)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Task Processing Mandate: Lightweight Simplicity & Explicit Limitations

In strict adherence to Principle 4 (Free-First) and Principle 6 (No Premature Infrastructure), `[STUDIO_NAME]` adopts **FastAPI `BackgroundTasks` as the lightweight MVP baseline (`RECOMMENDED`)**, rejecting external message brokers (Redis, Celery, RabbitMQ) for early-stage development.

However, the architecture explicitly documents the **inherent operational limitations** of FastAPI `BackgroundTasks`:
* **Process-Local**: Tasks execute entirely within the local web application process memory and ASGI event loop.
* **Not Durable**: If the server crashes, restarts, or deploys while a task is in flight, the task coroutine is permanently lost.
* **Not Suitable for Long-Running Work**: Heavy CPU tasks, long scraping jobs, or complex file transformations will block event loop threads and degrade web responsiveness.
* **Not a Persistent Queue**: It does not provide persistent message buffering, dead-letter exchanges, or guaranteed at-least-once delivery.
* **Scale-Triggered Architecture**: Distributed message brokers (Redis + Celery / ARQ / SQS) remain strictly classified as **Future / Scale-Triggered Architecture**, activated only when business volume or enterprise durability mandates it.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TASK PROCESSING EVOLUTIONARY HORIZONS                           │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ HORIZON               │ ARCHITECTURAL MECHANISM    │ INFRASTRUCTURE DEPENDENCIES       │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ **MVP Horizon**       │ FastAPI Native             │ **Zero extra infrastructure (₹0)**│
│                       │ `BackgroundTasks`          │ Process-local, non-durable tasks  │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ **Phase 2 Horizon**   │ Database-Backed Job Table  │ Microsoft SQL Server              │
│                       │ (`dbo.background_tasks`)   │ Polled durable retry queue        │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ **Future Horizon**    │ Distributed Queue          │ Redis / RabbitMQ / Cloud Queue    │
│                       │ (Celery / ARQ / SQS)       │ Multi-worker auto-scaling clusters│
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 2. MVP Task Inventory & Execution Mechanics

### A. Task Inventory (MVP Suite)
1. **`send_blueprint_delivery_email`**: Asynchronously dispatches the completed 18-section Solution Blueprint and recovery magic link to the lead's email upon progressive gating.
2. **`send_architect_triage_alert`**: Asynchronously alerts the studio's senior technical architects when a client submits a review request (`BD-010`).
3. **`purge_abandoned_sessions_job`**: Scheduled maintenance task purging uncompleted anonymous sessions in accordance with ratified data retention policy (`POLICY DECISION REQUIRED`).

### B. Execution Architecture: FastAPI `BackgroundTasks`
Tasks are registered within FastAPI route handlers and executed immediately after the HTTP response is committed to the client:
```python
# Conceptual Architecture Pattern
@router.post("/discovery/lead-unlock")
async def unlock_blueprint(
    data: LeadCaptureInput,
    background_tasks: BackgroundTasks,
    session: DiscoverySession = Depends(get_session)
):
    lead = lead_service.capture_lead(data, session)
    blueprint = blueprint_service.generate_blueprint(session)
    
    # Non-blocking async execution after HTTP 200 is emitted
    background_tasks.add_task(
        notification_service.send_blueprint_email, 
        recipient=lead.corporate_email, 
        blueprint_id=blueprint.id
    )
    return {"success": True, "message": "Blueprint unlocked"}
```

---

## 3. Resilience, Retries & Error Logging

1. **In-Process Error Isolation**: If an email delivery task fails due to third-party SMTP throttling, the failure is caught within the task wrapper and logged to structured application logs with `event="background_task_failed"`. It **never causes the client's HTTP request to fail or crash**.
2. **Retry Protocol**: Lightweight exponential backoff (3 attempts with 2s, 5s delays) is handled within the async task coroutine.
3. **Phase 2 Database-Backed Transition Trigger**: If daily diagnostic volume exceeds 500 completed sessions per day, or if strict zero-loss task durability is required for enterprise SLAs, the system will activate the `dbo.background_tasks` polling pattern.
