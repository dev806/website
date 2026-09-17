# Environment Configuration & Settings Management Specification

**Document ID:** `DOC-ARCH-021`  
**Classification:** DevOps & Security / Phase 4 Configuration Specification  
**Approved Decisions:** [BD-001](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-001), [BD-014](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-014), [BD-015](file:///d:/Project_website/docs/00-project/DECISION_LOG.md#dec-015)  
**Parent Framework:** [System Architecture](file:///d:/Project_website/docs/05-architecture/01-SYSTEM-ARCHITECTURE.md) | [Security Architecture](file:///d:/Project_website/docs/05-architecture/14-SECURITY-ARCHITECTURE.md)  
**Status:** CANONICAL SPECIFICATION  

---

## 1. Configuration Principles: Typed & Isolated

Application settings are managed using **Pydantic v2 `BaseSettings`** (`pydantic-settings`). 

This architecture guarantees:
1. **Strict Type Coercion**: Configuration values (ports, booleans, pool limits) are validated at application boot. Invalid types cause immediate, descriptive boot failures.
2. **Environment Isolation**: The same codebase runs across `development`, `testing`, `staging`, and `production` by changing only environment variables.
3. **Secret Hygiene**: Real secrets are never stored in version control or documentation.

---

## 2. Pydantic Settings Class Architecture (`app/config.py`)

```python
# Conceptual Architecture Pattern
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Literal

class Settings(BaseSettings):
    # Core Application
    app_name: str = "[STUDIO_NAME]"
    app_env: Literal["development", "testing", "staging", "production"] = "development"
    debug: bool = False
    secret_key: SecretStr = Field(..., min_length=32)
    base_url: str = "http://localhost:8000"

    # Database Persistence (Microsoft SQL Server)
    database_url: SecretStr
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_recycle: int = 1800

    # AI Gateway
    ai_gateway_mode: Literal["live", "mock"] = "live"
    ai_primary_model: str = "gemini-1.5-flash"
    ai_api_key: SecretStr
    ai_timeout_seconds: float = 10.0

    # Session & Cookie Security
    session_cookie_name: str = "studio_session_id"
    session_max_age_seconds: int = 2592000  # 30 days
    session_secure_cookie: bool = False     # True in production

    # Notifications & SMTP
    smtp_enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: SecretStr = SecretStr("")
    architect_alert_email: str = "architects@studio.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
```

---

## 3. Environment Variable Master Catalog

| Variable Name | Required | Default (Dev) | Production Purpose & Guidance |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | No | `[STUDIO_NAME]` | Display title across UI and email templates. |
| `APP_ENV` | Yes | `development` | Switches security flags, debug logging, and error envelopes. |
| `DEBUG` | No | `True` | Must be strictly `False` in production. |
| `SECRET_KEY` | **Yes** | None | 64-character random string used for HMAC session signing. |
| `BASE_URL` | Yes | `http://localhost:8000`| Canonical URL for generating email magic links. |
| `DATABASE_URL` | **Yes** | `mssql+aioodbc://...` | SQLAlchemy connection string to Microsoft SQL Server. |
| `AI_GATEWAY_MODE` | No | `mock` | `mock` uses local deterministic fixtures; `live` calls external API. |
| `AI_API_KEY` | **Yes (Live)**| None | Secure token for external AI provider (OpenAI, Anthropic, Google). |
| `SESSION_SECURE_COOKIE`| No | `False` | Sets `Secure=True` on cookies; requires HTTPS in production. |
| `SMTP_ENABLED` | No | `False` | Enables real outbound email dispatch for blueprints. |
| `ARCHITECT_ALERT_EMAIL`| Yes| None | Recipient address for high-priority client review requests. |
