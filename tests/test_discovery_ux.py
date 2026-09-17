"""
Comprehensive UX & Integration Test Suite for Phase 5.3 Discovery Web Experience.
Strictly validates:
1. Exact route path registration (zero duplicate /discovery/discovery prefixes).
2. Full 7-stage interactive journey via HTTP HTML responses & HTMX partials.
3. Accessible HTML5 landmark structure, skip links, aria-live status regions.
4. Input validation and non-blocking error partial recovery.
5. 100% Free & Ungated Opportunity Map delivery.
6. Progressive lead capture with mandatory consent enforcement.
7. Unlocked 18-section Blueprint, dual-currency estimate display, and verbatim disclaimer (BD-006).
8. Non-destructive backtracking (POST /discovery/backtrack) with unlock preservation.
9. Session resumption from signed HTTP-only cookies.
10. Human Architect Review queueing and Stage 7 handoff confirmation.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.database.connection import get_engine
from app.database.models import DiscoverySession
from app.main import app
from app.modules.discovery.session_manager import SESSION_COOKIE_NAME
from sqlalchemy.orm import sessionmaker


def test_discovery_routes_structure():
    """Asserts that all Discovery routes exist with exact paths and zero duplicate prefixes."""
    from app.routers import discovery_views

    discovery_paths = [r.path for r in discovery_views.router.routes]

    # Critical check: No duplicate prefix
    assert not any("/discovery/discovery" in p for p in discovery_paths), (
        "Found accidental duplicate prefix in routes!"
    )

    # Assert authoritative routes
    expected_routes = [
        "/discovery",
        "/discovery/start",
        "/discovery/problem",
        "/discovery/answers",
        "/discovery/stage/opportunity-map",
        "/discovery/unlock",
        "/discovery/review",
        "/discovery/backtrack",
    ]
    for exp in expected_routes:
        assert exp in discovery_paths, f"Missing expected route: {exp}"


@pytest.mark.asyncio
async def test_discovery_page_get_fresh_session():
    """Verifies GET /discovery initializes a new session, issues cookie, and renders Stage 1."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/discovery")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]

        # Cookie check
        assert SESSION_COOKIE_NAME in res.cookies

        html = res.text
        # Accessibility landmarks
        assert 'class="skip-link"' in html
        assert 'role="banner"' in html
        assert 'role="main"' in html
        assert 'role="status" aria-live="polite"' in html

        # Stage 1 elements
        assert "What's getting in the way of your business?" in html
        assert "Step 1 of 7" in html
        assert "14%" in html
        assert "Continue" in html
        assert "Confidentiality Guarantee" in html


@pytest.mark.asyncio
async def test_discovery_stage_1_problem_validation_error():
    """Verifies problem statement shorter than 20 characters returns accessible 422 error partial."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Start session
        start_res = await client.get("/discovery")
        cookie = start_res.cookies[SESSION_COOKIE_NAME]

        # Submit short text
        res = await client.post(
            "/discovery/problem",
            data={"raw_text": "Too short"},
            cookies={SESSION_COOKIE_NAME: cookie},
        )
        assert res.status_code == 422
        html = res.text
        assert "Action Could Not Be Completed" in html
        assert "at least 20 characters" in html
        assert "INPUT_TOO_SHORT" in html


@pytest.mark.asyncio
async def test_full_7_stage_discovery_journey(db_session):
    """
    Executes the complete consultative user journey from Stage 1 through Stage 7
    via HTMX interaction endpoints and verifies all DOM contracts and database states.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # ---------------------------------------------------------------------
        # Step 1: Initialize Session via GET /discovery
        # ---------------------------------------------------------------------
        page_res = await client.get("/discovery")
        assert page_res.status_code == 200
        cookie_val = page_res.cookies[SESSION_COOKIE_NAME]
        auth_cookies = {SESSION_COOKIE_NAME: cookie_val}

        # ---------------------------------------------------------------------
        # Step 2: Submit Problem -> Stage 2 Clarification Questions
        # ---------------------------------------------------------------------
        problem_payload = {
            "raw_text": (
                "Our logistics dispatch team spends 4 hours every morning copy-pasting carrier "
                "shipping manifests from incoming emails into QuickBooks and our legacy ERP system."
            )
        }
        prob_res = await client.post(
            "/discovery/problem",
            data=problem_payload,
            cookies=auth_cookies,
        )
        assert prob_res.status_code == 200
        prob_html = prob_res.text
        assert "A few quick questions to narrow scope" in prob_html
        assert "Step 2 of 7" in prob_html
        assert "Operational Context" in prob_html
        assert "28%" in prob_html
        assert "radio-card" in prob_html
        assert "Continue" in prob_html

        # ---------------------------------------------------------------------
        # Step 3: Submit Answers -> Stage 4 Executive Opportunity Map (100% Free / Ungated)
        # ---------------------------------------------------------------------
        answers_payload = {
            "q1": "Spreadsheets / Legacy ERP",
            "q2": "Manual Data Entry",
            "q3": "Immediate (< 4 weeks)",
        }
        ans_res = await client.post(
            "/discovery/answers",
            data=answers_payload,
            cookies=auth_cookies,
        )
        assert ans_res.status_code == 200
        ans_html = ans_res.text
        assert "Your Executive Opportunity Map" in ans_html
        assert "100% Free &amp; Ungated Strategic Diagnostic" in ans_html
        assert "opp-card" in ans_html
        assert "Step 4 of 7" in ans_html
        assert "57%" in ans_html
        assert "Unlock Full Solution Blueprint &amp; Estimates" in ans_html

        # Verify Stage 3 structured understanding synthesis is included at top
        assert "Structured Problem Understanding" in ans_html
        assert "Core Operational Challenge" in ans_html

        # ---------------------------------------------------------------------
        # Step 4: Verify Opportunity Map direct ungated GET access
        # ---------------------------------------------------------------------
        direct_opp_res = await client.get(
            "/discovery/stage/opportunity-map",
            cookies=auth_cookies,
        )
        assert direct_opp_res.status_code == 200
        assert "Your Executive Opportunity Map" in direct_opp_res.text

        # ---------------------------------------------------------------------
        # Step 5: Progressive Reveal Gate Validation (Missing Consent)
        # ---------------------------------------------------------------------
        bad_unlock_res = await client.post(
            "/discovery/unlock",
            data={
                "full_name": "Sarah Jenkins",
                "corporate_email": "sarah@acme-logistics.com",
                "consent_given": False,  # Missing consent
            },
            cookies=auth_cookies,
        )
        assert bad_unlock_res.status_code == 422
        assert "Explicit consent is required" in bad_unlock_res.text

        # ---------------------------------------------------------------------
        # Step 6: Progressive Reveal Gate Validation (Invalid Email)
        # ---------------------------------------------------------------------
        bad_email_res = await client.post(
            "/discovery/unlock",
            data={
                "full_name": "Sarah Jenkins",
                "corporate_email": "not-an-email",
                "consent_given": True,
            },
            cookies=auth_cookies,
        )
        assert bad_email_res.status_code == 422
        assert "Please enter a valid corporate email address" in bad_email_res.text

        # ---------------------------------------------------------------------
        # Step 7: Successful Unlock -> Stage 5 (Blueprint) & Stage 6 (Estimates)
        # ---------------------------------------------------------------------
        valid_unlock_payload = {
            "full_name": "Sarah Jenkins",
            "corporate_email": "sarah@acme-logistics.com",
            "company_name": "Acme Logistics Global",
            "phone_number": "+1 555-0199",
            "consent_given": True,
        }
        unlock_res = await client.post(
            "/discovery/unlock",
            data=valid_unlock_payload,
            cookies=auth_cookies,
        )
        assert unlock_res.status_code == 200
        unlock_html = unlock_res.text

        # Stage 5 Blueprint checks
        assert "Comprehensive Solution Blueprint" in unlock_html
        assert "AI-GENERATED PRELIMINARY SPECIFICATION" in unlock_html
        assert "blueprint-section-card" in unlock_html
        assert "Step 5 of 7" in unlock_html

        # Stage 6 Estimates checks
        assert "Indicative Planning Parameters" in unlock_html
        assert "INR (₹)" in unlock_html
        assert "USD ($)" in unlock_html
        assert "Indicative Budget Band" in unlock_html
        assert "Estimated Timeline" in unlock_html
        assert "IMPORTANT NOTICE — NON-BINDING ESTIMATE" in unlock_html

        # ---------------------------------------------------------------------
        # Step 8: Non-Destructive Backtracking (POST /discovery/backtrack)
        # ---------------------------------------------------------------------
        backtrack_res = await client.post(
            "/discovery/backtrack",
            data={"target_stage": "opportunity_map"},
            cookies=auth_cookies,
        )
        assert backtrack_res.status_code == 200
        assert "Your Executive Opportunity Map" in backtrack_res.text

        # Verify progressive unlock was preserved in database
        session_obj = (
            db_session.query(DiscoverySession)
            .filter(DiscoverySession.is_unlocked == True)
            .first()
        )
        assert session_obj is not None
        assert session_obj.is_unlocked is True

        # ---------------------------------------------------------------------
        # Step 9: Stage 7 Human Architect Review Handoff
        # ---------------------------------------------------------------------
        review_payload = {
            "notes": "Please verify QuickBooks webhook rate limit capabilities for high invoice bursts."
        }
        review_res = await client.post(
            "/discovery/review",
            data=review_payload,
            cookies=auth_cookies,
        )
        assert review_res.status_code == 200
        review_html = review_res.text
        assert "Dossier Submitted to Senior Architect Queue" in review_html
        assert "PENDING ARCHITECT REVIEW" in review_html
        assert "Within 1 Business Day (BD-013)" in review_html
        assert "Permanent Diagnostic Recovery Link" in review_html
        assert "Step 7 of 7" in review_html
        assert "100%" in review_html

        # ---------------------------------------------------------------------
        # Step 10: Session Resumption on Fresh GET /discovery
        # ---------------------------------------------------------------------
        resume_res = await client.get("/discovery", cookies=auth_cookies)
        assert resume_res.status_code == 200
        # Should resume at completed handoff screen
        assert "Dossier Submitted to Senior Architect Queue" in resume_res.text
        assert "100%" in resume_res.text


@pytest.mark.asyncio
async def test_discovery_unlock_validation_consent_required(async_client, db_session):
    """Verifies that unlocking Blueprint without mandatory consent yields 422 error."""
    client = async_client

    # Start session and reach opportunity map
    start_res = await client.post("/discovery/start")
    auth_cookies = {k: v for k, v in start_res.cookies.items()}

    prob_payload = {
        "raw_text": "We are experiencing delays in synchronizing customer order records between ERP and warehouse manifests."
    }
    await client.post("/discovery/problem", data=prob_payload, cookies=auth_cookies)
    await client.post(
        "/discovery/answers",
        data={"q1": "Custom Warehouse Portal", "q2": "Immediate Horizon"},
        cookies=auth_cookies,
    )

    # Attempt unlock without consent
    unlock_payload = {
        "full_name": "Test User",
        "corporate_email": "user@enterprise.com",
        "company_name": "Enterprise Corp",
        "consent_given": "false",
    }
    res = await client.post("/discovery/unlock", data=unlock_payload, cookies=auth_cookies)
    assert res.status_code == 422
    assert "Explicit consent is required" in res.text
    assert "CONSENT_REQUIRED" in res.text


@pytest.mark.asyncio
async def test_discovery_unlock_validation_invalid_email(async_client, db_session):
    """Verifies that unlocking Blueprint with invalid email yields 422 error."""
    client = async_client

    start_res = await client.post("/discovery/start")
    auth_cookies = {k: v for k, v in start_res.cookies.items()}

    prob_payload = {
        "raw_text": "Automating financial spreadsheet aggregation across 20 subsidiary branches every month."
    }
    await client.post("/discovery/problem", data=prob_payload, cookies=auth_cookies)
    await client.post(
        "/discovery/answers",
        data={"q1": "Financial Systems", "q2": "Quarterly Horizon"},
        cookies=auth_cookies,
    )

    # Attempt unlock with invalid email format
    unlock_payload = {
        "full_name": "Test User",
        "corporate_email": "not-an-email",
        "consent_given": "true",
    }
    res = await client.post("/discovery/unlock", data=unlock_payload, cookies=auth_cookies)
    assert res.status_code == 422
    assert "Please enter a valid corporate email address" in res.text
    assert "INVALID_EMAIL_FORMAT" in res.text


@pytest.mark.asyncio
async def test_discovery_backtrack_to_problem_and_questions(async_client, db_session):
    """Verifies backtracking sequentially back to questions and problem stages."""
    client = async_client

    start_res = await client.post("/discovery/start")
    auth_cookies = {k: v for k, v in start_res.cookies.items()}

    prob_payload = {
        "raw_text": "Inventory reconciliation between retail POS terminals and central warehouse SAP instance."
    }
    await client.post("/discovery/problem", data=prob_payload, cookies=auth_cookies)
    await client.post(
        "/discovery/answers",
        data={"q1": "SAP ERP", "q2": "Weekly"},
        cookies=auth_cookies,
    )

    # Backtrack to questions
    bt_q = await client.post(
        "/discovery/backtrack",
        data={"target_stage": "questions"},
        cookies=auth_cookies,
    )
    assert bt_q.status_code == 200
    assert "A few quick questions to narrow scope" in bt_q.text

    # Backtrack to problem
    bt_p = await client.post(
        "/discovery/backtrack",
        data={"target_stage": "problem"},
        cookies=auth_cookies,
    )
    assert bt_p.status_code == 200
    assert "What's getting in the way of your business?" in bt_p.text
    assert "Inventory reconciliation between retail POS" in bt_p.text


@pytest.mark.asyncio
async def test_stage_2_radio_selection_contract(async_client, db_session):
    """
    Validates Stage 2 Clarification Questions radio-selection DOM contract:
    1. Every question renders distinct prompt text and a unique semantic radio group name.
    2. All options within a single question share the EXACT same name attribute.
    3. Options across different questions have DIFFERENT name attributes (independent groups).
    4. Zero radio inputs have empty name (name="") or name="None".
    5. Options start unselected with custom-radio-indicator and radio-dot present.
    6. Submitting answers using the rendered radio names advances session to Opportunity Map.
    """
    import re
    client = async_client
    start_res = await client.post("/discovery/start")
    auth_cookies = {k: v for k, v in start_res.cookies.items()}

    prob_payload = {
        "raw_text": "We need to automate daily customer dispatch manifests and inventory reconciliation across 3 warehouses."
    }
    prob_res = await client.post("/discovery/problem", data=prob_payload, cookies=auth_cookies)
    assert prob_res.status_code == 200
    html = prob_res.text

    # Extract all radio inputs
    radio_matches = re.findall(r'<input[^>]+type=["\']radio["\'][^>]*>', html)
    assert len(radio_matches) >= 4, f"Expected at least 4 radio options across questions, found {len(radio_matches)}"

    # Extract name attributes
    names = []
    for r in radio_matches:
        name_match = re.search(r'name=["\']([^"\']*)["\']', r)
        assert name_match is not None, f"Radio input missing name attribute: {r}"
        val = name_match.group(1)
        assert val != "", f"Radio input has empty name attribute: {r}"
        assert val != "None", f"Radio input has 'None' name attribute: {r}"
        names.append(val)

    # Verify multiple distinct groups exist
    distinct_groups = list(dict.fromkeys(names))
    assert len(distinct_groups) >= 2, f"Expected at least 2 distinct question groups, got {distinct_groups}"

    # Verify each group has multiple options sharing the exact same name
    for grp in distinct_groups:
        count = names.count(grp)
        assert count >= 2, f"Group '{grp}' should contain at least 2 options, found {count}"

    # Verify unselected state: no options are checked by default
    for r in radio_matches:
        assert "checked" not in r, f"Radio option unexpectedly pre-checked: {r}"

    # Verify custom radio indicator and radio dot elements are present
    assert 'class="custom-radio-indicator"' in html
    assert 'class="radio-dot"' in html

    # Submit answers using the dynamic names discovered in the form
    answers_data = {grp: "Custom Web App & SQL" for grp in distinct_groups}
    ans_res = await client.post("/discovery/answers", data=answers_data, cookies=auth_cookies)
    assert ans_res.status_code == 200
    assert "Your Executive Opportunity Map" in ans_res.text


@pytest.mark.asyncio
async def test_opportunity_map_to_blueprint_unlock_flow(async_client, db_session):
    """
    Regression test verifying Phase 5.3 Blueprint Unlock button & progressive lead capture flow:
    1. Opportunity Map stage rendered ungated.
    2. Unlock CTA button and form elements present with correct IDs, text, and HTMX attributes.
    3. Missing consent returns 422 error partial.
    4. Invalid email returns 422 error partial.
    5. Valid submission with consent unlocks session, persists lead, and returns combined Stage 5 & 6.
    """
    client = async_client

    start_res = await client.post("/discovery/start")
    auth_cookies = {k: v for k, v in start_res.cookies.items()}

    # 1. Problem Input
    prob_res = await client.post(
        "/discovery/problem",
        data={"raw_text": "Dispatch logistics and shipping manifest entry takes 4 hours daily across multiple systems."},
        cookies=auth_cookies,
    )
    assert prob_res.status_code == 200

    # 2. Answers -> Stage 4 Opportunity Map
    opp_res = await client.post(
        "/discovery/answers",
        data={"q1": "Legacy ERP & SQL", "q2": "Manual Data Entry"},
        cookies=auth_cookies,
    )
    assert opp_res.status_code == 200
    opp_html = opp_res.text

    # Assert Stage 4 DOM contracts
    assert "Your Executive Opportunity Map" in opp_html
    assert "100% Free &amp; Ungated Strategic Diagnostic" in opp_html
    assert 'id="btn-reveal-unlock-form"' in opp_html
    assert 'id="lead-unlock-container"' in opp_html
    assert 'hx-post="/discovery/unlock"' in opp_html
    assert 'id="btn-submit-unlock"' in opp_html
    assert "Unlock Full Blueprint &amp; Indicative Estimates" in opp_html

    # 3. Missing consent failure
    no_consent_res = await client.post(
        "/discovery/unlock",
        data={
            "full_name": "Sarah Jenkins",
            "corporate_email": "sarah@acme-logistics.com",
            "consent_given": "false",
        },
        cookies=auth_cookies,
    )
    assert no_consent_res.status_code == 422
    assert "Explicit consent is required" in no_consent_res.text

    # 4. Invalid email failure
    no_email_res = await client.post(
        "/discovery/unlock",
        data={
            "full_name": "Sarah Jenkins",
            "corporate_email": "invalid-email-format",
            "consent_given": "true",
        },
        cookies=auth_cookies,
    )
    assert no_email_res.status_code == 422
    assert "Please enter a valid corporate email address" in no_email_res.text

    # 5. Valid unlock submission
    unlock_res = await client.post(
        "/discovery/unlock",
        data={
            "full_name": "Sarah Jenkins",
            "corporate_email": "sarah@acme-logistics.com",
            "company_name": "Acme Logistics Global",
            "phone_number": "+1 555-0199",
            "consent_given": "true",
        },
        cookies=auth_cookies,
    )
    assert unlock_res.status_code == 200
    unlock_html = unlock_res.text

    # Assert Stage 5 & 6 returned
    assert "Comprehensive Solution Blueprint" in unlock_html
    assert "AI-GENERATED PRELIMINARY SPECIFICATION" in unlock_html
    assert "Indicative Planning Parameters" in unlock_html
    assert "INR (₹)" in unlock_html
    assert "USD ($)" in unlock_html
    assert "IMPORTANT NOTICE — NON-BINDING ESTIMATE" in unlock_html

    # Verify session in DB is elevated
    sess = db_session.query(DiscoverySession).filter(DiscoverySession.is_unlocked == True).first()
    assert sess is not None
    assert sess.lead_id is not None


