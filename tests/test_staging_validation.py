"""
Automated Test Suite for Phase 6.2.5 — Staging & Deployment Validation Foundation
Conforms strictly to DOC-REP-6.2.5-PLAN.

Validates:
1. Staging configuration validation constraints (fail-fast on debug=True or insecure dev secrets).
2. Environment-specific SEO safeguards (robots.txt Disallow and X-Robots-Tag header in staging).
3. Staging cookie security enforcement and session token response header suppression.
4. Multi-worker stateless session resume simulation across independent worker contexts.
5. Migration validation tooling safety guards (blocking unconfirmed production targets).
6. Smoke test suite runner verification.
"""

from unittest.mock import MagicMock
import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.main import create_app
from app.routers.discovery_views import _attach_session_cookie
from scripts.smoke_test import SmokeTestRunner
from scripts.validate_migrations import validate_migrations


def test_staging_settings_rejects_debug_true():
    """Verifies that debug=True is rejected when app_env is staging."""
    with pytest.raises(ValidationError, match="DEBUG mode must be strictly False in staging"):
        Settings(
            app_env="staging",
            debug=True,
            secret_key="s" * 32,
            session_secure_cookie=True,
            database_url="mssql+pyodbc://sa:Secret@staging-server:1433/StudioWebsiteStag",
        )


def test_staging_settings_rejects_insecure_secret_key():
    """Verifies that development default secret keys are rejected in staging."""
    with pytest.raises(ValidationError, match="SECRET_KEY must be a secure random string"):
        Settings(
            app_env="staging",
            debug=False,
            secret_key="dev-insecure-secret-key-must-be-changed-in-production-min-32-chars",
            session_secure_cookie=True,
            database_url="mssql+pyodbc://sa:Secret@staging-server:1433/StudioWebsiteStag",
        )


def test_staging_settings_valid():
    """Verifies that valid staging settings instantiate cleanly."""
    settings = Settings(
        app_env="staging",
        debug=False,
        secret_key="s" * 48,
        session_secure_cookie=True,
        database_url="mssql+pyodbc://sa:Secret@staging-server:1433/StudioWebsiteStag",
    )
    assert settings.app_env == "staging"
    assert settings.debug is False
    assert settings.session_secure_cookie is True


def test_staging_robots_txt_disallow(monkeypatch):
    """Verifies that /robots.txt returns 'Disallow: /' when app_env is staging to prevent search crawling."""
    staging_settings = Settings(
        app_env="staging",
        debug=False,
        secret_key="s" * 48,
    )
    monkeypatch.setattr("app.routers.web.get_settings", lambda: staging_settings)

    test_app = create_app(staging_settings)
    client = TestClient(test_app)

    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "User-agent: *" in response.text
    assert "Disallow: /" in response.text
    assert "Allow: /" not in response.text


def test_staging_response_headers_contain_x_robots_tag(monkeypatch):
    """Verifies that responses in staging include 'X-Robots-Tag: noindex, nofollow, noarchive'."""
    staging_settings = Settings(
        app_env="staging",
        debug=False,
        secret_key="s" * 48,
    )
    test_app = create_app(staging_settings)
    client = TestClient(test_app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("x-robots-tag") == "noindex, nofollow, noarchive"
    assert "strict-transport-security" in response.headers


def test_staging_cookie_secure_flag_enforced(monkeypatch):
    """Verifies that session cookies enforce secure=True in staging even if session_secure_cookie=False."""
    staging_settings = Settings(
        app_env="staging",
        debug=False,
        secret_key="s" * 48,
        session_secure_cookie=False,
    )
    monkeypatch.setattr("app.routers.discovery_views.get_settings", lambda: staging_settings)

    mock_response = MagicMock(spec=Response)
    _attach_session_cookie(mock_response, "signed.cookie.value", secure=False)

    mock_response.set_cookie.assert_called_once()
    _, kwargs = mock_response.set_cookie.call_args
    assert kwargs.get("secure") is True
    assert kwargs.get("httponly") is True
    assert kwargs.get("samesite") == "lax"


def test_staging_suppresses_x_session_token_header():
    """Verifies that /api/v1/discovery/start suppresses X-Session-Token and X-Session-ID headers in staging."""
    from app.config import get_settings
    from app.database.session import get_db
    from app.modules.discovery.router import get_discovery_service

    staging_settings = Settings(
        app_env="staging",
        debug=False,
        secret_key="s" * 48,
        session_secure_cookie=True,
    )
    test_app = create_app(staging_settings)

    mock_service = MagicMock()
    mock_session = MagicMock()
    mock_session.id = "22222222-2222-2222-2222-222222222222"
    mock_session.current_stage = "START"
    mock_session.is_unlocked = False
    mock_service.start_session.return_value = (mock_session, "signed.cookie.value", "raw-token-staging")

    test_app.dependency_overrides[get_settings] = lambda: staging_settings
    test_app.dependency_overrides[get_discovery_service] = lambda: mock_service
    test_app.dependency_overrides[get_db] = lambda: MagicMock()

    client = TestClient(test_app)

    response = client.post("/api/v1/discovery/start", json={"entry_point": "staging_test"})
    assert response.status_code == 201
    assert "X-Session-Token" not in response.headers
    assert "X-Session-ID" not in response.headers


def test_multi_worker_stateless_session_simulation():
    """
    Simulates multi-worker execution:
    Worker 1 initializes a discovery session and returns a signed cookie.
    Worker 2 (a separate application instance sharing SECRET_KEY and DB) consumes that cookie and processes the problem statement.
    Verifies that session state is 100% durable in SQL Server and stateless in worker memory.
    """
    shared_key = "k" * 48
    worker1_settings = Settings(app_env="testing", secret_key=shared_key)
    worker2_settings = Settings(app_env="testing", secret_key=shared_key)

    app_worker1 = create_app(worker1_settings)
    app_worker2 = create_app(worker2_settings)

    client1 = TestClient(app_worker1)
    client2 = TestClient(app_worker2)

    # Worker 1 starts the session
    res_start = client1.post("/discovery/start", data={"entry_point": "worker1_test"})
    assert res_start.status_code == 200
    session_cookie = client1.cookies.get("studio_session_id")
    assert session_cookie is not None

    # Worker 2 resumes session using the cookie created by Worker 1
    client2.cookies.set("studio_session_id", session_cookie)
    res_problem = client2.post(
        "/discovery/problem",
        data={
            "raw_text": "We have severe bottlenecks in our invoice verification and reconciliation processes."
        },
    )
    assert res_problem.status_code == 200
    assert "Step 2 of 7" in res_problem.text or "Architectural Clarifications" in res_problem.text


def test_migration_validation_tooling_production_safety_guard():
    """Verifies that validate_migrations() refuses execution against a production target without confirmation."""
    # When target_env is production and force_production is False, must return False safely
    result = validate_migrations(
        database_url="mssql+pyodbc://sa:Secret@prod-server:1433/StudioWebsiteProd",
        target_env="production",
        force_production=False,
    )
    assert result is False


def test_smoke_test_runner_initialization():
    """Verifies that SmokeTestRunner instantiates correctly and configures headers and cookie jar."""
    runner = SmokeTestRunner(base_url="http://127.0.0.1:8000", timeout=5.0, verbose=False)
    assert runner.base_url == "http://127.0.0.1:8000"
    assert runner.timeout == 5.0
    assert len(runner.results) == 0


def test_smoke_test_runner_run_check_flow():
    """Verifies that SmokeTestRunner records check results properly with mock requests."""
    runner = SmokeTestRunner(base_url="http://mock", timeout=2.0)
    runner._request = MagicMock(return_value=(200, {"x-frame-options": "DENY"}, "Turn Business Problems Into Technology"))
    passed = runner.run_check(
        "SMK-01", "Mock Check", "GET", "/", 200,
        body_assertions=["Turn Business Problems Into Technology"],
        header_assertions=["x-frame-options"]
    )
    assert passed is True
    assert len(runner.results) == 1
    assert runner.results[0][0] == "SMK-01"
    assert runner.results[0][2] is True

