"""
Configuration & Settings Unit Tests for [STUDIO_NAME]
"""

import pytest
from pydantic import ValidationError
from app.config import Settings, get_settings


def test_settings_defaults():
    """Verifies default settings are configured properly."""
    settings = get_settings()
    assert settings.app_name == "[STUDIO_NAME]"
    assert settings.database_pool_size == 10
    assert settings.database_max_overflow == 20
    assert settings.ai_gateway_mode == "mock"
    assert settings.ai_timeout_seconds == 10.0


def test_settings_secret_masking():
    """Verifies secret key and database credentials are masked by default."""
    settings = get_settings()
    repr_str = repr(settings)
    assert "dev-insecure-secret-key" not in repr_str
    assert "**********" in repr_str


def test_settings_database_url_resolution():
    """Verifies that in testing mode, get_database_url_str returns StudioWebsiteTest."""
    settings = Settings(app_env="testing")
    db_url = settings.get_database_url_str()
    assert "StudioWebsiteTest" in db_url


def test_settings_secret_key_minimum_length():
    """Verifies that short secret keys are rejected."""
    with pytest.raises(ValidationError):
        Settings(secret_key="too-short")
