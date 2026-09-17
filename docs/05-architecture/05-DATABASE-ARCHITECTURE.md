# Microsoft SQL Server Database Architecture Specification

**Document ID:** `DOC-ARCH-005`  
**Classification:** Database Architecture / Phase 4 Persistence Design  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [ADR-004](file:///d:/Project_website/docs/05-architecture/02-ARCHITECTURE-DECISION-RECORDS.md#adr-004)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Executive Mandate: Microsoft SQL Server + SSMS (`CST-CNF-008`)

In strict adherence to Owner Constraint `CST-CNF-008`, the primary development and testing database engine is **Microsoft SQL Server Developer Edition or SQL Server Express**, managed visually via **SQL Server Management Studio (SSMS)**.

The architecture eliminates all unnecessary multi-database complexity:
- **Zero PostgreSQL** during local development.
- **Zero SQLite** for testing. All automated tests execute against a dedicated local SQL Server database instance (`StudioWebsiteTest`).
- **Zero Redis or NoSQL** databases in local development. Relational tables combined with SQL Server's native JSON support handle all state, caching, and background task persistence at **₹0 infrastructure cost**.

---

## 2. Database Topology & Isolation Boundaries

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LOCAL SQL SERVER DATABASE TOPOLOGY                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   SQL SERVER LOCAL INSTANCE: (localdb)\MSSQLLocalDB  or  localhost:1433                │
│                                                                                        │
│   ┌─────────────────────────────────────┐   ┌──────────────────────────────────────┐   │
│   │ 1. `StudioWebsiteDev`               │   │ 2. `StudioWebsiteTest`               │   │
│   │ • Primary local development DB.     │   │ • Dedicated test database.           │   │
│   │ • Holds active migration history.   │   │ • Cleared / rolled back in Pytest.   │   │
│   │ • Inspected visually via SSMS.      │   │ • Guarantees 100% dialect parity.    │   │
│   └─────────────────────────────────────┘   └──────────────────────────────────────┘   │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Schema Organization & Naming Conventions

### A. Schema Partitioning
Tables are grouped logically under a clean relational schema strategy:
* **`dbo`**: Core application tables (`dbo.discovery_sessions`, `dbo.leads`, `dbo.solution_blueprints`).

### B. Standard Naming Conventions
* **Table Names**: Plural, lowercase with snake_case (e.g. `discovery_sessions`, `solution_blueprints`, `leads`).
* **Column Names**: Lowercase with snake_case (e.g. `session_id`, `created_at`, `is_deleted`).
* **Primary Keys**: Explicitly named `id` (as `UNIQUEIDENTIFIER`) or `<entity>_id` on foreign keys.
* **Foreign Key Constraints**: Standardized prefix `FK_<child_table>_<parent_table>_<column>`.
* **Indexes**: Standardized prefix `IX_<table_name>_<column_name>`.

---

## 4. Normalization Strategy & Hybrid JSON Storage

The persistence layer applies a **hybrid relational + document storage pattern**:
1. **Strict 3NF for Commercial & Core Entities**: `leads`, `review_requests`, and `discovery_sessions` are strictly normalized to ensure transactional integrity, auditability, and fast relational joins.
2. **Native JSON Columns (`NVARCHAR(MAX)`) for Polymorphic Synthesis**: Unstructured, highly polymorphic AI outputs (such as dynamic clarification question trees, opportunity graph nodes, and the 18-section architectural blueprint) are persisted as validated JSON strings inside `NVARCHAR(MAX)` columns. SQL Server natively validates and queries these via `ISJSON()` and `JSON_VALUE()`.

---

## 5. Primary Keys, Indexing & Concurrency Engine

### A. Primary Key Architecture (`UNIQUEIDENTIFIER`)
* All entities utilize 128-bit Universally Unique Identifiers (`UNIQUEIDENTIFIER` / UUID4) generated client-side by Python (`uuid.uuid4()`).
* **Clustering Strategy**: To prevent B-tree fragmentation associated with random UUIDs in SQL Server, tables utilize non-clustered primary keys with a sequential clustered identity column (`surrogate_seq BIGINT IDENTITY(1,1)`), or utilize sequential GUID generation where appropriate.

### B. Indexing Philosophy
* **Lookup Foreign Keys**: Every foreign key column (`session_id`, `lead_id`) possesses an explicit non-clustered index.
* **Filter & Query Optimization**: Non-clustered index on `leads(email)` and `discovery_sessions(session_token_hash)` for sub-millisecond lookups.
* **Filtered Indexes for Soft Deletes**:
  ```sql
  CREATE NONCLUSTERED INDEX IX_discovery_sessions_active 
  ON dbo.discovery_sessions(created_at) 
  WHERE is_deleted = 0;
  ```

### C. Concurrency: Read Committed Snapshot Isolation (RCSI)
To eliminate lock contention and blocking between background AI synthesis writes and client-side HTMX reads, the SQL Server database must have **Read Committed Snapshot Isolation** enabled:
```sql
ALTER DATABASE StudioWebsiteDev SET READ_COMMITTED_SNAPSHOT ON;
ALTER DATABASE StudioWebsiteDev SET ALLOW_SNAPSHOT_ISOLATION ON;
```
Under RCSI, read operations do not acquire shared locks, guaranteeing that readers never block writers and writers never block readers.

---

## 6. Auditability, Soft Deletion & Timestamps

Every table in the database inherits a standard set of temporal and audit columns via an SQLAlchemy declarative mixin:
* **`created_at`**: `DATETIMEOFFSET` with UTC timezone (`GETUTCDATE()`), immutable.
* **`updated_at`**: `DATETIMEOFFSET` with UTC timezone, updated automatically via application triggers or ORM events.
* **`is_deleted`**: `BIT DEFAULT 0`, supporting non-destructive soft deletion.
* **`deleted_at`**: `DATETIMEOFFSET NULL`, recording the exact timestamp of deletion.

---

## 7. Connection Pooling & Driver Configuration (`TECHNICAL VALIDATION REQUIRED`)

### A. SQLAlchemy Connection Pool Strategy
* **Pool Implementation**: SQLAlchemy `QueuePool` maintaining persistent, pre-authenticated database connections to reduce TCP handshake latency.
* **Pool Sizing (Candidate Baseline)**:
  - `pool_size = 10` (Normal baseline connections).
  - `max_overflow = 20` (Surge capacity for concurrent diagnostic traffic).
  - `pool_recycle = 1800` (Recycles connections every 30 minutes to prevent stale timeouts).
  - `pool_pre_ping = True` (Verifies connection liveness before leasing to a request).

### B. ODBC Driver & Concurrency Architecture (`TECHNICAL VALIDATION REQUIRED`)
* **Recommended Driver**: **Microsoft ODBC Driver 18 for SQL Server**.
* **Driver Concurrency Mode (`AOQ-003`)**:
  - *Candidate 1*: `aioodbc` (`mssql+aioodbc`) — native async asyncio ODBC connection.
  - *Candidate 2*: `pyodbc` (`mssql+pyodbc`) — synchronous driver executed via FastAPI's `asyncio.to_thread` worker pool.
  - **Status**: `TECHNICAL VALIDATION REQUIRED`. The choice between `aioodbc` and `pyodbc` + threadpool must not assume `aioodbc` is automatically superior. A dedicated technical spike in Phase 5 Sprint 0 will benchmark connection stability, thread safety, and event-loop latency under Windows 11 before committing to the final driver.
* **Dialect & Migration Compatibility (`TECHNICAL VALIDATION REQUIRED`)**:
  - The combination of SQLAlchemy 2.0 MSSQL dialect, `aioodbc`, Alembic schema migrations, and Read Committed Snapshot Isolation (RCSI) on Windows 11 is **theoretically supported but requires empirical test suite validation**.
  - Untested combinations must not be represented as proven.
* **Candidate Connection String Format (Windows Localhost)**:
  ```text
  mssql+aioodbc://localhost/StudioWebsiteDev?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&Encrypt=no&TrustServerCertificate=yes
  ```
* **Authentication Modes**: Both Windows Integrated Authentication (`Trusted_Connection=yes`) and SQL Server standard authentication (`sa` / local user) are supported candidate options requiring validation during developer environment setup.
