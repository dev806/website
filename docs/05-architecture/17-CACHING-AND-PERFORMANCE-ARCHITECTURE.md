# Performance & Caching Architecture Specification

**Document ID:** `DOC-ARCH-017`  
**Classification:** Performance Engineering / Phase 4 Caching Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [ADR-012](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md#adr-012)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Performance Engineering Principles & Integrity Rules

In strict compliance with project governance:
> **GOVERNANCE RULE:** The system **never claims unsupported performance guarantees** (such as *"guaranteed sub-second AI responses"*, *"FCP < 0.8s"*, or *"99.99% uptime"*). All performance parameters are treated as **empirical targets to be benchmarked under real load**.

Furthermore:
* **Caching as an Optimization, Not a Dependency**: Caching is treated strictly as an optimization strategy, not a mandatory infrastructure dependency.
* **No Redis for MVP Caching**: Introducing an external Redis cache server solely for web response caching is explicitly rejected for MVP.
* **Preferred Tier Hierarchy**: The architecture prioritizes:
  1. Client browser caching via HTTP headers
  2. Framework-level and in-process memory caching (`functools.lru_cache`)
  3. Static solution and service catalog caching
  4. Database buffer pool management (RCSI in SQL Server)

The architecture optimizes for **fast time-to-first-byte (TTFB), minimal client memory footprint, zero client-side hydration delays, and low perceived waiting time**.

---

## 2. Multi-Tier Performance & Caching Topology

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 4-TIER CACHING TOPOLOGY                               │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ TIER                  │ CACHING MECHANISM          │ APPLIED SURFACES & TARGET ASSETS  │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ 1. Client Browser     │ HTTP `Cache-Control`       │ Static assets (`/static/css/*`,   │
│                       │ headers + asset hashing.   │ `/static/js/*`). 1-year max-age.  │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ 2. Application Memory │ Python `functools.lru_cache`│ Static solution blueprint catalog,│
│ (In-Process)          │ in worker memory.          │ service pillar models. (0ms read).│
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ 3. Database Engine    │ SQL Server Buffer Pool +   │ Filtered non-clustered indexes;   │
│ (Persistence)         │ Read Committed Snapshot.   │ zero-lock snapshot reads (RCSI).  │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ 4. Perceived AI UX    │ Asynchronous HTMX skeleton │ Diagnostic synthesis; eliminates  │
│                       │ loaders + DOM morphing.    │ blank-screen cognitive friction.  │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 3. Database Query Optimization & Indexing Hygiene

In Microsoft SQL Server (`CST-CNF-008`), high-throughput query performance is achieved via four explicit optimizations:
1. **Zero Table-Scanning on Diagnostics**: Every query executed during the 7-stage discovery flow utilizes indexed key lookups (`session_token_hash`, `session_id`).
2. **Read Committed Snapshot Isolation (RCSI)**: Eliminates reader-writer blocking. Read queries (e.g. checking session state) never wait for active database writes.
3. **Filtered Indexes for Active Data**: Soft-deleted records (`is_deleted = 1`) are excluded from active search indexes via `WHERE is_deleted = 0`, keeping index B-trees compact.
4. **Connection Re-Use (QueuePool)**: SQLAlchemy maintains pre-spawned, verified database connections, eliminating the high TCP and TLS handshake cost of creating a new SQL Server connection per web request.

---

## 4. AI Latency Management & Perceived Performance

External LLM API latency ($1.5\text{s}$ to $4.0\text{s}$) represents the largest latency bottleneck in the system. The architecture mitigates this through:
1. **Bounded Input Token Budgets**: User problem text is strictly capped (recommended 50–300 words, maximum 20KB). Shorter prompts process significantly faster on commercial API endpoints.
2. **Low-Temperature Determinism**: `temperature = 0.1` ensures rapid, deterministic token sampling without model dithering.
3. **Pulsing Skeleton States**: While HTMX waits for the server response, the browser immediately swaps in an accessible animated skeleton placeholder (`hx-indicator="#loading-spinner"`), visually reassuring the user that synthesis is actively in progress.
