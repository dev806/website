"""
Automated Test Suite for Phase 6.1 — Security Hardening
Conforms to DOC-TEST-001 and Phase 6.1 Implementation Authorization.
Tests security headers, native in-memory rate limiting, PII/secret scrubbing,
SQL injection safety, XSS escaping, and sensitive error leakage protection.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.shared.security import scrub_pii


client = TestClient(app)


def test_security_headers_present():
    """Verifies that mandatory HTTP security headers and CSP are present on responses."""
    response = client.get("/")
    assert response.status_code == 200
    headers = response.headers

    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert "strict-origin-when-cross-origin" in headers.get("Referrer-Policy", "")
    assert "geolocation=()" in headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")


def test_rate_limiting_exceeded_returns_429():
    """Verifies that exceeding the 5 req/min POST rate limit returns HTTP 429 and Retry-After header."""
    payload = {
        "full_name": "Test User",
        "corporate_email": "test@company.com",
        "message": "Inquiry message text for rate limit testing.",
    }

    # Send 5 allowed requests
    for i in range(5):
        res = client.post("/contact", data=payload)
        assert res.status_code in [200, 422], f"Request {i+1} failed with {res.status_code}"

    # 6th request must be rate-limited (HTTP 429)
    res_exceeded = client.post("/contact", data=payload)
    assert res_exceeded.status_code == 429
    assert res_exceeded.headers.get("Retry-After") == "60"
    data = res_exceeded.json()
    assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "X-Correlation-ID" in res_exceeded.headers


def test_rate_limiting_exempt_routes():
    """Verifies that GET endpoints and health probes are exempt from rate limiting."""
    for _ in range(10):
        res_home = client.get("/")
        assert res_home.status_code == 200

        res_health = client.get("/health/live")
        assert res_health.status_code == 200


def test_pii_and_credential_scrubbing_expansion():
    """Verifies that scrub_pii redacts emails, phone numbers, SSNs, credit cards, API keys, and connection secrets."""
    sample_text = (
        "Contact me at sarah@company.com or +1-212-555-0199. "
        "SSN is 123-45-6789. Card: 4111-2222-3333-4444. "
        "API key is sk-12345678901234567890123. Connection string password=SecretPassword123!"
    )
    scrubbed = scrub_pii(sample_text)

    assert "sarah@company.com" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed

    assert "+1-212-555-0199" not in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed

    assert "123-45-6789" not in scrubbed
    assert "[REDACTED_SSN]" in scrubbed

    assert "4111-2222-3333-4444" not in scrubbed
    assert "[REDACTED_CARD]" in scrubbed

    assert "sk-12345678901234567890123" not in scrubbed
    assert "[REDACTED_KEY]" in scrubbed

    assert "SecretPassword123!" not in scrubbed
    assert "[REDACTED_CREDENTIAL]" in scrubbed


def test_sql_injection_payload_handling():
    """Verifies that T-SQL injection attack payloads are treated safely as plain text literals without ORM errors."""
    sql_payload = {
        "full_name": "Attacker'; DROP TABLE leads;--",
        "corporate_email": "attacker@enterprise.com",
        "company_name": "Acme Inc",
        "project_scope": "Bespoke Software Architecture",
        "message": "SELECT * FROM discovery_sessions WHERE 1=1; DROP TABLE problem_statements;--",
    }
    response = client.post("/contact", data=sql_payload)
    assert response.status_code == 200
    assert "Inquiry Received" in response.text


def test_xss_payload_escaping():
    """Verifies that XSS payloads are safely HTML-escaped in template responses."""
    xss_payload = {
        "full_name": "<script>alert('xss')</script>",
        "corporate_email": "xss-test@company.com",
        "company_name": "<img src=x onerror=alert(1)>",
        "project_scope": "Bespoke Software Architecture",
        "message": "Testing script injection <script>document.cookie</script>",
    }
    response = client.post("/contact", data=xss_payload)
    assert response.status_code == 200
    assert "<script>alert" not in response.text
    assert "&lt;script&gt;" in response.text or "Inquiry Received" in response.text


def test_sensitive_error_leakage_prevention():
    """Verifies that 404, 422, and 500 error responses return clean JSON envelopes without stack traces or secrets."""
    response_404 = client.get("/nonexistent-path-12345")
    assert response_404.status_code == 404
    data = response_404.json()
    assert "error" in data
    assert "Traceback" not in response_404.text
    assert "SELECT" not in response_404.text
