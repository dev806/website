"""
Configuration Management Module for [STUDIO_NAME]
Validates and exposes typed environment settings using Pydantic v2 Settings.
"""

from functools import lru_cache
from typing import Literal
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DEV_DATABASE_URL = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteDev%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)

DEFAULT_TEST_DATABASE_URL = (
    "mssql+pyodbc:///?odbc_connect="
    "Driver%3D%7BODBC+Driver+18+for+SQL+Server%7D%3B"
    "Server%3D.%5CSQLEXPRESS%3BDatabase%3DStudioWebsiteTest%3B"
    "Trusted_Connection%3Dyes%3BTrustServerCertificate%3Dyes%3B"
)


class Settings(BaseSettings):
    """Core application settings with environment variable resolution."""

    # Application Metadata & Runtime Mode
    app_name: str = Field(default="[STUDIO_NAME]", description="Public studio display name")
    app_env: Literal["development", "testing", "staging", "production"] = Field(
        default="development", description="Current operating environment"
    )
    debug: bool = Field(default=False, description="Debug mode flag; strictly False in production")
    base_url: str = Field(default="http://localhost:8000", description="Canonical application base URL")

    # Cryptographic & Security Secrets
    secret_key: SecretStr = Field(
        default=SecretStr("dev-insecure-secret-key-must-be-changed-in-production-min-32-chars"),
        min_length=32,
        description="HMAC signing key for session tokens and cookies",
    )

    # Database Persistence (Microsoft SQL Server 2022 Express)
    database_url: SecretStr = Field(
        default=SecretStr(DEFAULT_DEV_DATABASE_URL),
        description="SQLAlchemy connection URI for SQL Server",
    )
    database_pool_size: int = Field(default=10, ge=1, le=50, description="SQLAlchemy connection pool size")
    database_max_overflow: int = Field(default=20, ge=0, le=100, description="Max overflow connections")
    database_pool_recycle: int = Field(default=1800, ge=60, description="Connection recycle interval in seconds")

    # AI Gateway Settings
    ai_gateway_mode: Literal["live", "mock"] = Field(
        default="mock", description="AI execution mode (mock for local development and unit tests)"
    )
    ai_timeout_seconds: float = Field(default=10.0, ge=0.1, le=60.0, description="AI gateway timeout threshold")
    ai_primary_model: str = Field(default="studio-mock-v1", description="Target model identifier")

    # Observability & Telemetry Settings
    log_format: Literal["text", "json"] = Field(
        default="text", description="Log output format (text or json)"
    )
    slow_query_threshold_ms: float = Field(
        default=500.0, ge=10.0, le=60000.0, description="Slow query threshold in milliseconds"
    )
    slow_request_threshold_ms: float = Field(
        default=1000.0, ge=10.0, le=60000.0, description="Slow HTTP request threshold in milliseconds"
    )

    # Session & Cookie Security
    session_cookie_name: str = Field(default="studio_session_id", description="Session cookie name")
    session_max_age_seconds: int = Field(default=2592000, description="Session TTL (default 30 days)")
    session_secure_cookie: bool = Field(default=False, description="Requires HTTPS cookie flag in production")

    # Notifications & Alerts
    smtp_enabled: bool = Field(default=False, description="Outbound SMTP dispatcher toggle")
    architect_alert_email: str = Field(
        default="architects@studio.internal", description="Inbox for senior architect evaluation requests"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_database_url_str(self) -> str:
        """Returns the unmasked database connection string for SQLAlchemy engine initialization."""
        # In testing mode, if using default dev URL, point to test database
        raw_url = self.database_url.get_secret_value()
        if self.app_env == "testing" and "StudioWebsiteDev" in raw_url:
            return DEFAULT_TEST_DATABASE_URL
        return raw_url


@lru_cache
def get_settings() -> Settings:
    """Returns the cached application settings instance."""
    return Settings()
