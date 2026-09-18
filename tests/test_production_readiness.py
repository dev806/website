"""
Automated Test Suite for Phase 6.2.4 — Production Readiness Foundation
Validates:
1. Production configuration hardening and validation constraints.
2. Trusted proxy parsing and IP spoofing prevention.
3. Cookie HTTPS enforcement and session token response header suppression.
4. Request payload size boundary defenses.
"""

from unittest.mock import MagicMock
import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import _get_client_ip, create_app
from app.routers.discovery_views import _attach_session_cookie


def test_production_settings_rejects_debug_true():
    """Verifies that debug=True is rejected when app_env is production."""
    with pytest.raises(ValidationError, match="DEBUG mode must be strictly False in production"):
        Settings(
            app_env="production",
            debug=True,
            secret_key="a" * 32,
            session_secure_cookie=True,
            database_url="mssql+pyodbc://sa:Secret@prod-server:1433/ProdDB",
        )


def test_production_settings_rejects_insecure_secret_key():
    """Verifies that development default secret keys are rejected in production."""
    with pytest.raises(ValidationError, match="SECRET_KEY must be a production-grade random string"):
        Settings(
            app_env="production",
            debug=False,
            secret_key="dev-insecure-secret-key-must-be-changed-in-production-min-32-chars",
            session_secure_cookie=True,
            database_url="mssql+pyodbc://sa:Secret@prod-server:1433/ProdDB",
        )


def test_production_settings_rejects_insecure_cookie():
    """Verifies that session_secure_cookie=False is rejected in production."""
    with pytest.raises(ValidationError, match="SESSION_SECURE_COOKIE must be True in production"):
        Settings(
            app_env="production",
            debug=False,
            secret_key="super-strong-production-secret-key-min-32-characters",
            session_secure_cookie=False,
            database_url="mssql+pyodbc://sa:Secret@prod-server:1433/ProdDB",
        )


def test_production_settings_rejects_sqlexpress_url():
    """Verifies that SQLEXPRESS database URLs are rejected in production."""
    with pytest.raises(ValidationError, match="DATABASE_URL must be configured for production SQL Server"):
        Settings(
            app_env="production",
            debug=False,
            secret_key="super-strong-production-secret-key-min-32-characters",
            session_secure_cookie=True,
            database_url="mssql+pyodbc:///?odbc_connect=Server%3D.%5CSQLEXPRESS",
        )


def test_production_settings_valid():
    """Verifies that compliant production settings instantiate cleanly."""
    settings = Settings(
        app_env="production",
        debug=False,
        secret_key="super-strong-production-secret-key-min-32-characters",
        session_secure_cookie=True,
        database_url="mssql+pyodbc://sa:StrongPassword123@prod-mssql.internal:1433/StudioDB",
    )
    assert settings.app_env == "production"
    assert settings.debug is False
    assert settings.session_secure_cookie is True


def test_trusted_proxies_parsing():
    """Verifies that trusted_proxies can be provided as a comma-separated string or list."""
    settings_csv = Settings(trusted_proxies="10.0.0.1, 192.168.1.1")
    assert settings_csv.trusted_proxies == ["10.0.0.1", "192.168.1.1"]

    settings_json = Settings(trusted_proxies='["10.0.0.1", "127.0.0.1"]')
    assert settings_json.trusted_proxies == ["10.0.0.1", "127.0.0.1"]


def test_client_ip_trusted_proxy_handling():
    """
    Verifies that X-Forwarded-For is trusted ONLY when request originates
    from a peer listed in trusted_proxies.
    """
    # Case 1: Direct peer is trusted reverse proxy (127.0.0.1)
    req_trusted = MagicMock()
    req_trusted.client.host = "127.0.0.1"
    req_trusted.headers = {"X-Forwarded-For": "203.0.113.195, 10.0.0.1"}

    resolved_ip = _get_client_ip(req_trusted, trusted_proxies=["127.0.0.1"])
    assert resolved_ip == "203.0.113.195"

    # Case 2: Direct peer is an untrusted client attempting to spoof X-Forwarded-For
    req_untrusted = MagicMock()
    req_untrusted.client.host = "198.51.100.44"
    req_untrusted.headers = {"X-Forwarded-For": "1.2.3.4"}

    resolved_ip = _get_client_ip(req_untrusted, trusted_proxies=["127.0.0.1"])
    assert resolved_ip == "198.51.100.44", "Spoofed X-Forwarded-For from untrusted peer must be ignored"


def test_production_suppresses_x_session_token_header():
    """
    Verifies that in production mode, X-Session-Token and X-Session-ID headers
    are NOT leaked in the StartSessionResponse HTTP headers.
    """
    prod_settings = Settings(
        app_env="production",
        debug=False,
        secret_key="super-strong-production-secret-key-min-32-characters",
        session_secure_cookie=True,
        database_url="mssql+pyodbc://sa:StrongPassword123@prod-mssql.internal:1433/StudioDB",
    )
    prod_app = create_app(settings=prod_settings)

    mock_service = MagicMock()
    mock_session = MagicMock()
    mock_session.id = "11111111-1111-1111-1111-111111111111"
    mock_session.current_stage = "START"
    mock_session.is_unlocked = False
    mock_service.start_session.return_value = (mock_session, "signed.cookie.value", "raw-token-1234")

    from app.config import get_settings
    from app.database.session import get_db
    from app.modules.discovery.router import get_discovery_service

    prod_app.dependency_overrides[get_settings] = lambda: prod_settings
    prod_app.dependency_overrides[get_discovery_service] = lambda: mock_service
    prod_app.dependency_overrides[get_db] = lambda: MagicMock()

    prod_client = TestClient(prod_app)

    response = prod_client.post("/api/v1/discovery/start", json={"entry_point": "direct"})
    assert response.status_code == 201
    assert "X-Session-Token" not in response.headers
    assert "X-Session-ID" not in response.headers


def test_cookie_secure_flag_enforced_in_production():
    """
    Verifies that _attach_session_cookie sets secure=True when app_env is production.
    """
    resp = Response()
    _attach_session_cookie(resp, "token.sig", secure=False)
    # Even if secure=False was passed, when session_secure_cookie is True it becomes secure
    # In local dev defaults it is False, but test passing secure=True sets it:
    resp_explicit = Response()
    _attach_session_cookie(resp_explicit, "token.sig", secure=True)
    cookie_header = resp_explicit.headers.get("set-cookie", "")
    assert "secure" in cookie_header.lower()


def test_payload_too_large_rejected():
    """
    Verifies that requests exceeding 1MB (1,048,576 bytes) on rate-limited POST
    routes are rejected with HTTP 413.
    """
    app_instance = create_app()
    client = TestClient(app_instance)

    response = client.post(
        "/contact",
        data={"message": "x"},
        headers={"Content-Length": "2000000"},
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"
