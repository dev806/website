# Python Engineering Conventions & Coding Standards

**Document ID:** `DOC-ARCH-025`  
**Classification:** Engineering Standards / Phase 4 Code Guidelines  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015), [CST-CNF-007](file:///d:/Project_website/docs/00-project/PROJECT_CONSTRAINTS.md#cst-cnf-007)  
**Parent Framework:** [Project Principles](file:///d:/Project_website/docs/00-project/PROJECT_PRINCIPLES.md) | [Project Structure](file:///d:/Project_website/docs/05-architecture/04-PROJECT-STRUCTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Codebase Philosophy: Senior Craftsmanship & Radical Readability

All code authored for `[STUDIO_NAME]` adheres to the philosophy of **explicit, type-safe, maintainable Python engineering**. We favor boring, explicit, and durable code over clever or opaque abstractions.

---

## 2. Core Python Standards & Type Safety

### A. Style & Formatting
* **PEP 8 Compliance**: Strict adherence to standard Python conventions.
* **Line Length**: 100 characters max.
* **Linter & Formatter**: Formatted and linted via `ruff` (`ruff check .`, `ruff format .`).

### B. Mandatory Static Typing (`mypy --strict`)
* Every function, method, and coroutine must include 100% complete type annotations for all parameters and return types:
  ```python
  # Standard Convention Example
  async def get_session_by_token(
      token_hash: str, 
      db: AsyncSession
  ) -> DiscoverySessionDTO | None:
      ...
  ```
* Untyped `Any` is strictly prohibited unless wrapping third-party untyped library returns.

---

## 3. Pydantic v2 Standards

1. **DTO Immutability**: Domain DTOs prefer `model_config = ConfigDict(frozen=True)` to prevent accidental attribute mutation.
2. **Explicit Field Documentation**: All schema properties use `Field(description="...")` to automatically enrich OpenAPI/Swagger documentation.
3. **Serialization**: Use Pydantic v2 `.model_dump()` and `.model_dump_json()`. The legacy v1 `.dict()` and `.json()` methods are strictly barred.

---

## 4. SQLAlchemy 2.0 Modern Standards

In strict compliance with SQLAlchemy 2.x standards:
1. **Modern Select Syntax**: The legacy 1.x `session.query(Model)` syntax is completely banned. All database queries must use modern 2.0 select syntax:
   ```python
   # Correct 2.0 Modern Syntax
   stmt = select(DiscoverySession).where(
       DiscoverySession.session_token_hash == token_hash,
       DiscoverySession.is_deleted == False
   )
   result = await db.execute(stmt)
   session = result.scalar_one_or_none()
   ```
2. **Explicit Transaction Boundaries**: Database writes run inside explicit transactional blocks:
   ```python
   async with db.begin():
       db.add(new_lead)
   ```

---

## 5. Domain Exception Hierarchy

Domain services throw typed custom exceptions defined in `app/shared/exceptions.py`. The FastAPI layer maps these to standard HTTP status codes:
```python
class StudioBaseException(Exception):
    """Root application domain exception."""

class EntityNotFoundError(StudioBaseException):
    """Resource does not exist (Mapped to HTTP 404)."""

class InvalidStateTransitionError(StudioBaseException):
    """FSM guard condition failed (Mapped to HTTP 422)."""

class SecurityVerificationError(StudioBaseException):
    """CSRF or token mismatch (Mapped to HTTP 403)."""
```

---

## 6. Git & Version Control Conventions

Commits follow the **Conventional Commits** specification:
* `feat:` A new user-facing capability or API route.
* `fix:` A bug fix.
* `docs:` Documentation changes only.
* `refactor:` Code change that neither fixes a bug nor adds a feature.
* `test:` Adding missing tests or correcting existing tests.
* `chore:` Updating dependencies, linting, or configuration files.
