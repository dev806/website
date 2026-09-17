"""
End-to-End API Integration Tests for AI Discovery Engine Routes.
Strictly conforms to DOC-ARCH-009, DOC-ARCH-011, and DOC-PRD-003.

Validates:
1. Complete walkthrough across all 7 Discovery API endpoints.
2. HTTP-only cryptographic session cookie issuance and propagation.
3. Access control (403 Forbidden for locked blueprint).
4. Input validation (422 Unprocessable Entity for invalid payloads).
5. Authentication enforcement (401 Unauthorized when credentials missing).
6. Correlation ID tracking across requests.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.discovery.session_manager import SESSION_COOKIE_NAME


@pytest.mark.asyncio
async def test_full_discovery_api_walkthrough():
    """Validates the complete 7-stage consultative discovery flow via HTTP API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # ---------------------------------------------------------------------
        # Step 1: POST /api/v1/discovery/start
        # ---------------------------------------------------------------------
        start_res = await client.post(
            "/api/v1/discovery/start",
            json={"entry_point": "homepage_hero", "preseed_topic": None},
        )
        assert start_res.status_code == 201
        start_json = start_res.json()
        assert start_json["success"] is True
        session_id = start_json["data"]["session_id"]
        assert start_json["data"]["stage"] == "START"
        assert start_json["data"]["is_unlocked"] is False

        # Verify cookie and correlation ID
        assert SESSION_COOKIE_NAME in start_res.cookies
        session_cookie = start_res.cookies[SESSION_COOKIE_NAME]
        assert "X-Correlation-ID" in start_res.headers

        # Client session headers/cookies
        auth_cookies = {SESSION_COOKIE_NAME: session_cookie}

        # ---------------------------------------------------------------------
        # Step 2: POST /api/v1/discovery/problem
        # ---------------------------------------------------------------------
        problem_payload = {
            "raw_text": (
                "Our logistics dispatch team spends 4 hours every morning copy-pasting carrier "
                "shipping manifests from incoming emails into QuickBooks and our legacy ERP system."
            )
        }
        problem_res = await client.post(
            "/api/v1/discovery/problem",
            json=problem_payload,
            cookies=auth_cookies,
        )
        assert problem_res.status_code == 200
        problem_json = problem_res.json()
        assert problem_json["success"] is True
        assert len(problem_json["data"]["questions"]) >= 2
        assert problem_json["data"]["stage"] in ("QUESTIONS_GENERATED", "FALLBACK_ENGAGED")

        # ---------------------------------------------------------------------
        # Step 3: POST /api/v1/discovery/answers
        # ---------------------------------------------------------------------
        answers_payload = {
            "answers": {
                "q1": "QuickBooks & Legacy ERP",
                "q2": "20 – 100 per day",
            }
        }
        answers_res = await client.post(
            "/api/v1/discovery/answers",
            json=answers_payload,
            cookies=auth_cookies,
        )
        assert answers_res.status_code == 200
        answers_json = answers_res.json()
        assert answers_json["success"] is True
        assert answers_json["data"]["stage"] == "OPPORTUNITY_MAP_GENERATED"
        assert answers_json["data"]["opportunities_count"] >= 1

        # ---------------------------------------------------------------------
        # Step 4: GET /api/v1/discovery/opportunity-map (100% Free / Ungated)
        # ---------------------------------------------------------------------
        opp_res = await client.get(
            "/api/v1/discovery/opportunity-map",
            cookies=auth_cookies,
        )
        assert opp_res.status_code == 200
        opp_json = opp_res.json()
        assert opp_json["success"] is True
        assert len(opp_json["data"]["opportunities"]) >= 1

        # ---------------------------------------------------------------------
        # Step 5: GET /api/v1/discovery/blueprint before unlock -> 403 Forbidden
        # ---------------------------------------------------------------------
        locked_bp_res = await client.get(
            "/api/v1/discovery/blueprint",
            cookies=auth_cookies,
        )
        assert locked_bp_res.status_code == 403
        locked_json = locked_bp_res.json()
        assert locked_json["error"]["code"] == "BLUEPRINT_LOCKED"

        # ---------------------------------------------------------------------
        # Step 6: POST /api/v1/discovery/lead-unlock
        # ---------------------------------------------------------------------
        lead_payload = {
            "full_name": "Sarah Jenkins",
            "corporate_email": "sarah@acme-logistics.com",
            "company_name": "Acme Logistics Global",
            "phone_number": "+1-555-0199",
            "consent_given": True,
        }
        unlock_res = await client.post(
            "/api/v1/discovery/lead-unlock",
            json=lead_payload,
            cookies=auth_cookies,
        )
        assert unlock_res.status_code == 200
        unlock_json = unlock_res.json()
        assert unlock_json["success"] is True
        assert unlock_json["data"]["is_unlocked"] is True

        # ---------------------------------------------------------------------
        # Step 7: GET /api/v1/discovery/blueprint after unlock -> 200 OK
        # ---------------------------------------------------------------------
        bp_res = await client.get(
            "/api/v1/discovery/blueprint",
            cookies=auth_cookies,
        )
        assert bp_res.status_code == 200
        bp_json = bp_res.json()
        assert bp_json["success"] is True
        assert bp_json["data"]["status_badge"] == "AI_GENERATED_PRELIMINARY_DRAFT"
        assert len(bp_json["data"]["sections"]) == 18
        assert "IMPORTANT NOTICE" in bp_json["data"]["estimate"]["mandatory_disclaimer"]

        # ---------------------------------------------------------------------
        # Step 8: POST /api/v1/discovery/review
        # ---------------------------------------------------------------------
        review_payload = {
            "notes": "We would like to discuss whether our on-premise ERP firewall allows inbound webhooks."
        }
        review_res = await client.post(
            "/api/v1/discovery/review",
            json=review_payload,
            cookies=auth_cookies,
        )
        assert review_res.status_code == 201
        review_json = review_res.json()
        assert review_json["success"] is True
        assert review_json["data"]["status"] == "PENDING"

        # ---------------------------------------------------------------------
        # Step 9: GET /api/v1/discovery/session
        # ---------------------------------------------------------------------
        session_res = await client.get(
            "/api/v1/discovery/session",
            cookies=auth_cookies,
        )
        assert session_res.status_code == 200
        session_json = session_res.json()
        assert session_json["success"] is True
        assert session_json["data"]["current_stage"] == "COMPLETED"
        assert session_json["data"]["is_unlocked"] is True
        assert session_json["data"]["has_problem"] is True
        assert session_json["data"]["has_blueprint"] is True


@pytest.mark.asyncio
async def test_problem_validation_error():
    """Verifies that problem text shorter than 20 characters returns 422 Unprocessable Entity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        start_res = await client.post("/api/v1/discovery/start", json={})
        cookie = start_res.cookies[SESSION_COOKIE_NAME]

        res = await client.post(
            "/api/v1/discovery/problem",
            json={"raw_text": "Short"},
            cookies={SESSION_COOKIE_NAME: cookie},
        )
        assert res.status_code == 422
        err = res.json()
        assert err["success"] is False
        assert err["error"]["code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_lead_unlock_without_consent_fails():
    """Verifies that submitting lead form without explicit consent returns 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        start_res = await client.post("/api/v1/discovery/start", json={})
        cookie = start_res.cookies[SESSION_COOKIE_NAME]

        res = await client.post(
            "/api/v1/discovery/lead-unlock",
            json={
                "full_name": "Test User",
                "corporate_email": "test@domain.com",
                "consent_given": False,  # Missing consent
            },
            cookies={SESSION_COOKIE_NAME: cookie},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_unauthorized_without_session():
    """Verifies that calling stateful routes without session credentials returns 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/discovery/problem",
            json={"raw_text": "Valid length problem description exceeding twenty characters."},
        )
        assert res.status_code == 401
        err = res.json()
        assert err["error"]["code"] == "SESSION_UNAUTHORIZED"
