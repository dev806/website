# Testing & Quality Assurance Architecture Specification

**Document ID:** `DOC-ARCH-019`  
**Classification:** Quality Assurance / Phase 4 Test Engineering  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-005](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-005), [BD-006](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-006), [BD-010](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-010), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-008](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-008)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Database Architecture](file:///d:/Project_website/docs/05-architecture/05-DATABASE-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Testing Philosophy & Dialect Parity

In strict accordance with Owner Constraint `CST-CNF-008`, the test architecture enforces **absolute database dialect parity**:
- **Zero SQLite for Testing**: The system completely rejects testing against in-memory SQLite. Testing against SQLite masks SQL Server specific behaviors (T-SQL syntax, `DATETIMEOFFSET`, `UNIQUEIDENTIFIER`, transaction locks).
- **Dedicated SQL Server Test Database**: All integration tests execute against a dedicated local test database instance: **`StudioWebsiteTest`**.
- **Transactional Rollback Isolation**: Every test case runs inside an isolated database transaction that rolls back automatically upon test completion, guaranteeing pristine state with zero cross-test contamination.
- **Deterministic AI Testing**: Unit and CI tests **never make live network calls to external paid LLM APIs**. All AI interactions are tested via deterministic mock fixtures verifying Pydantic schema contracts.

---

## 2. The Test Pyramid Topology

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE TEST PYRAMID TOPOLOGY                              │
├───────────────────────┬────────────────────────────┬───────────────────────────────────┤
│ TEST TIER             │ SCOPE & COVERAGE           │ EXECUTION SPEED & ENVIRONMENT     │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 1: Unit Tests    │ Sizing formulas, PII       │ Pure in-memory Python (< 50ms).   │
│                       │ scrubbers, state guards.   │ Zero external dependencies.       │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 2: Integration   │ SQLAlchemy queries,        │ Local `StudioWebsiteTest`         │
│ Tests                 │ migrations, session state. │ SQL Server instance (< 200ms).    │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 3: API Contracts │ FastAPI routes, HTMX partial│ FastAPI `TestClient` asserting    │
│                       │ swaps, CSRF validation.    │ HTTP status codes & envelopes.    │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 4: AI Contracts  │ Mocked LLM payloads into   │ Validates Pydantic schema parsing │
│                       │ Pydantic DTO instances.    │ without external API token costs. │
├───────────────────────┼────────────────────────────┼───────────────────────────────────┤
│ Tier 5: End-to-End    │ Complete 7-stage user      │ Simulated full user journey from  │
│ User Flows            │ diagnostic to lead review. │ problem input to architect queue. │
└───────────────────────┴────────────────────────────┴───────────────────────────────────┘
```

---

## 3. Pytest Fixture Architecture (`tests/conftest.py`)

The automated testing framework relies on modular Pytest fixtures:

### A. Database Session Fixture (SQL Server Transaction Rollback)
```python
# Conceptual Pytest Fixture Architecture
@pytest.fixture(scope="function")
def db_session():
    # Connects to local dedicated test database
    engine = create_engine(TEST_DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()
    
    # Binds session to the transactional boundary
    session = Session(bind=connection)
    yield session
    
    # Guaranteed rollback ensures zero test data persistence
    session.close()
    transaction.rollback()
    connection.close()
```

### B. Mock AI Gateway Fixture
```python
@pytest.fixture
def mock_ai_gateway():
    gateway = Mock(spec=AIGatewayInterface)
    gateway.extract_structured_data.return_value = StructuredProblemContextDTO(
        core_challenge="Automating carrier invoice extraction",
        complexity_tier="MEDIUM",
        flagged_unknowns=["ERP API limits"]
    )
    return gateway
```

---

## 4. Key Verification Test Suites

1. **State Machine Integrity Tests (`tests/unit/test_state_machine.py`)**: Asserts that invalid state transitions (e.g. attempting to jump from `START` directly to `BLUEPRINT_GENERATED`) throw `InvalidStateTransitionError`.
2. **Estimation Formula Tests (`tests/unit/test_estimation.py`)**: Asserts that budget and timeline calculations produce exact, confidence-banded numbers matching test fixtures, and that the mandatory legal disclaimer (`BD-006`) is always attached.
3. **PII Sanitizer Tests (`tests/unit/test_security.py`)**: Feeds test strings containing Visa credit cards, passwords, and IDs, asserting that outputs are cleanly redacted before reaching the AI gateway.
4. **HTMX Partial Swap Tests (`tests/api/test_discovery_routes.py`)**: Asserts that requests with `HX-Request: true` return lightweight HTML fragments rather than the full `base.html` layout.
5. **Database Migration Parity Tests (`tests/integration/test_migrations.py`)**: Executes `alembic upgrade head` followed by `alembic downgrade base` on `StudioWebsiteTest` to verify clean schema evolution.
