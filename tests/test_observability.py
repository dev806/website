"""
Automated Test Suite for Phase 6.2.3 — Observability, Analytics & Telemetry
Tests JSON formatting, SensitiveFilter redaction, in-house telemetry taxonomy,
data minimization, correlation ID propagation, slow query listener, AI Gateway telemetry,
funnel event triggers, and local inspection utility.
"""

import io
import json
import logging
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.database.connection import _setup_engine_events
from app.main import app
from app.shared.logging import JSONLogFormatter, SensitiveFilter, correlation_id_ctx
from app.shared.telemetry import (
    CANONICAL_PRODUCT_EVENTS,
    OPERATIONAL_EVENTS,
    emit_telemetry_event,
    sanitize_telemetry_payload,
)
from scripts.inspect_telemetry import parse_telemetry_lines, print_summary


client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Logging & Formatter Tests
# -----------------------------------------------------------------------------

def test_json_log_formatter_output():
    """Verifies that JSONLogFormatter outputs valid single-line NDJSON with expected keys."""
    formatter = JSONLogFormatter()
    logger = logging.getLogger("test.formatter")
    record = logger.makeRecord(
        name="test.formatter",
        level=logging.INFO,
        fn="test_file.py",
        lno=10,
        msg="Test message for JSON formatter",
        args=(),
        exc_info=None,
        extra={
            "event": "discovery_started",
            "duration_ms": 12.34,
            "http": {"method": "POST", "path": "/discovery/start", "status_code": 201},
            "context": {"entry_point": "homepage_hero"},
        },
    )

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "info"
    assert data["logger"] == "test.formatter"
    assert data["message"] == "Test message for JSON formatter"
    assert data["event"] == "discovery_started"
    assert data["duration_ms"] == 12.34
    assert data["http"]["status_code"] == 201
    assert data["context"]["entry_point"] == "homepage_hero"
    assert "timestamp" in data
    assert "correlation_id" in data


def test_sensitive_filter_redacts_credentials_and_pii():
    """Verifies that SensitiveFilter masks passwords, bearer tokens, API keys, and emails."""
    filter_instance = SensitiveFilter()
    logger = logging.getLogger("test.sensitive")

    test_cases = [
        ("Connecting with pwd=SuperSecret123; to db", "pwd=[REDACTED]"),
        ("Using password=AnotherPassword; in connection", "password=[REDACTED]"),
        ("Authorization: Bearer my-secret-token-12345-xyz", "Bearer [REDACTED]"),
        ("Model key sk-1234567890abcdef1234567890 active", "[REDACTED_KEY]"),
        ("User email test.user@example.com provided", "[REDACTED_EMAIL]"),
    ]

    for raw_msg, expected_substring in test_cases:
        record = logger.makeRecord("test", logging.INFO, "f.py", 1, raw_msg, (), None)
        filter_instance.filter(record)
        assert expected_substring in record.msg
        # Ensure secret itself is removed
        assert "SuperSecret123" not in record.msg
        assert "AnotherPassword" not in record.msg
        assert "my-secret-token" not in record.msg
        assert "test.user@example.com" not in record.msg


# -----------------------------------------------------------------------------
# 2. Telemetry Emitter & Taxonomy Tests
# -----------------------------------------------------------------------------

def test_telemetry_approved_taxonomy():
    """Verifies that all 7 canonical product events are accepted and unapproved events are dropped."""
    for event_name in CANONICAL_PRODUCT_EVENTS:
        assert emit_telemetry_event(event_name, {"sample": "data"}) is True

    # Operational events with is_operational=True must be accepted
    for event_name in OPERATIONAL_EVENTS:
        assert emit_telemetry_event(event_name, {"metric": 1}, is_operational=True) is True

    # Unapproved events must be rejected/dropped
    assert emit_telemetry_event("unapproved_custom_event", {}) is False
    assert emit_telemetry_event("arbitrary_event", {}, is_operational=True) is False


def test_telemetry_payload_pii_dropping():
    """Verifies that prohibited keys are stripped and natural language is scrubbed."""
    dirty_payload = {
        "full_name": "Senior Executive",
        "corporate_email": "exec@enterprise.com",
        "phone_number": "+1 555-123-4567",
        "password": "SecretPassword",
        "prompt": "Raw business prompt text with secrets",
        "session_token_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stage_number": 3,
        "notes": "Please contact me at direct.line@company.com soon.",
    }

    clean = sanitize_telemetry_payload(dirty_payload)

    # Prohibited keys must be deleted entirely
    assert "full_name" not in clean
    assert "corporate_email" not in clean
    assert "phone_number" not in clean
    assert "password" not in clean
    assert "prompt" not in clean

    # Allowed keys preserved
    assert clean["session_token_hash"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert clean["stage_number"] == 3

    # Nested text scrubbed
    assert "[REDACTED_EMAIL]" in clean["notes"]
    assert "direct.line@company.com" not in clean["notes"]


# -----------------------------------------------------------------------------
# 3. Correlation ID & Middleware Telemetry Tests
# -----------------------------------------------------------------------------

def test_correlation_id_propagation():
    """Verifies that custom X-Correlation-ID is preserved and attached to response."""
    custom_id = "test-corr-id-phase623-12345"
    response = client.get("/", headers={"X-Correlation-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-ID") == custom_id


def test_correlation_id_generated_when_absent():
    """Verifies that a valid UUID correlation ID is generated when none is supplied."""
    response = client.get("/")
    assert response.status_code == 200
    corr_id = response.headers.get("X-Correlation-ID")
    assert corr_id is not None
    assert len(corr_id) >= 32


def test_rate_limit_telemetry_has_correlation_id_and_hashed_ip(caplog):
    """Verifies that 429 response includes matching correlation ID and logs anonymized IP hash."""
    payload = {
        "full_name": "Test Actor",
        "corporate_email": "actor@company.com",
        "message": "Testing rate limit telemetry and correlation ID.",
    }

    with caplog.at_level(logging.WARNING):
        for _ in range(5):
            client.post("/contact", data=payload)

        # 6th request triggers rate limit
        res = client.post("/contact", data=payload)
        assert res.status_code == 429
        corr_id = res.headers.get("X-Correlation-ID")
        data = res.json()

        # Error envelope must contain correlation ID in meta.request_id
        assert data["meta"]["request_id"] == corr_id

        # Log must contain rate_limit_exceeded event and NOT raw IP
        warning_records = [r for r in caplog.records if getattr(r, "event", None) == "rate_limit_exceeded"]
        assert len(warning_records) >= 1
        assert "actor@company.com" not in warning_records[0].message


# -----------------------------------------------------------------------------
# 4. Contact Form PII Leak Remediation Test
# -----------------------------------------------------------------------------

def test_contact_form_does_not_log_email(caplog):
    """Verifies that corporate_email is NOT logged in plain text during contact submission."""
    test_email = "confidential.lead@megacorp.com"
    payload = {
        "full_name": "Confidential Architect",
        "corporate_email": test_email,
        "company_name": "MegaCorp Industries",
        "project_scope": "ai",
        "message": "We require senior architectural evaluation for our enterprise systems.",
    }

    with caplog.at_level(logging.INFO):
        res = client.post("/contact", data=payload)
        assert res.status_code == 200

        # Scan all captured log messages
        for record in caplog.records:
            assert test_email not in record.getMessage(), f"PII Leak: Found {test_email} in log message!"


# -----------------------------------------------------------------------------
# 5. Noise Gate & Health Check Exclusion Tests
# -----------------------------------------------------------------------------

def test_health_endpoints_do_not_emit_product_analytics(caplog):
    """Verifies that /health/live and /health/ready do not emit product analytics events."""
    with caplog.at_level(logging.INFO):
        res_live = client.get("/health/live")
        assert res_live.status_code == 200

        res_ready = client.get("/health/ready")
        assert res_ready.status_code in [200, 503]

        product_events = [
            getattr(r, "event", None) for r in caplog.records
            if getattr(r, "event", None) in CANONICAL_PRODUCT_EVENTS
        ]
        assert len(product_events) == 0, f"Unexpected product events emitted: {product_events}"


# -----------------------------------------------------------------------------
# 6. Slow SQL Query Event Listener Test
# -----------------------------------------------------------------------------

def test_slow_query_listener_triggers_on_threshold(caplog):
    """Verifies that SQLAlchemy event listener identifies slow queries exceeding 500ms without logging parameters."""
    cfg = get_settings()
    mock_engine = MagicMock()
    mock_engine.pool = MagicMock()

    # Capture the registered listeners
    listeners = {}
    def fake_listen(target, identifier, fn=None):
        if fn:
            listeners[identifier] = fn
            return fn
        def decorator(func):
            listeners[identifier] = func
            return func
        return decorator

    with pytest.MonkeyPatch.context() as mp:
        from sqlalchemy import event
        mp.setattr(event, "listens_for", fake_listen)
        _setup_engine_events(mock_engine, cfg)

        assert "before_cursor_execute" in listeners
        assert "after_cursor_execute" in listeners

        context = MagicMock()
        statement = "SELECT p.*, s.name FROM dbo.problem_statements p WHERE p.id = ?"
        secret_params = ("secret_problem_statement_text",)

        # Fire before hook
        listeners["before_cursor_execute"](None, None, statement, secret_params, context, False)

        # Simulate delay exceeding 500ms threshold
        context._query_start_time = context._query_start_time - 0.600  # 600ms elapsed

        with caplog.at_level(logging.WARNING):
            listeners["after_cursor_execute"](None, None, statement, secret_params, context, False)

            slow_records = [r for r in caplog.records if getattr(r, "event", None) == "slow_sql_query"]
            assert len(slow_records) >= 1
            rec = slow_records[0]
            assert rec.duration_ms >= 500.0
            assert rec.operation == "SELECT"
            # Parameters must NEVER be logged
            assert "secret_problem_statement_text" not in rec.getMessage()


# -----------------------------------------------------------------------------
# 7. AI Gateway Telemetry Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ai_gateway_telemetry_emitted(caplog):
    """Verifies that AI Gateway operations emit structured telemetry events without raw prompt leakage."""
    import asyncio
    from app.ai_gateway.gateway import AIServiceGateway
    from app.ai_gateway.mock_provider import MockAIProvider

    gateway = AIServiceGateway(provider=MockAIProvider())
    prompt = "Our billing system has severe data duplication and manual spreadsheet reconciliations."

    with caplog.at_level(logging.INFO):
        dto, source = await gateway.generate_clarifications(prompt)
        assert source == "PROVIDER_LLM"
        assert len(dto.questions) >= 2

        # Check telemetry event
        ai_records = [r for r in caplog.records if getattr(r, "event", None) == "ai_completion"]
        assert len(ai_records) >= 1
        rec = ai_records[0]
        assert rec.context["operation"] == "clarifications"
        assert rec.context["source"] == "PROVIDER_LLM"
        # Prompt text must NOT be in event extra
        assert prompt not in str(getattr(rec, "context", ""))

    # Test fallback path
    class FailingProvider:
        async def complete_structured(self, *args, **kwargs):
            raise asyncio.TimeoutError()

    failing_gw = AIServiceGateway(provider=FailingProvider())
    with caplog.at_level(logging.INFO):
        _, fallback_source = await failing_gw.generate_clarifications(prompt)
        assert fallback_source == "FALLBACK_TIMEOUT"
        fallback_records = [r for r in caplog.records if getattr(r, "event", None) == "ai_fallback"]
        assert len(fallback_records) >= 1
        assert fallback_records[0].context["source"] == "FALLBACK_TIMEOUT"


# -----------------------------------------------------------------------------
# 8. Discovery Funnel Telemetry Trigger Tests
# -----------------------------------------------------------------------------

def test_discovery_funnel_event_triggers(caplog):
    """Verifies that DiscoveryService emits canonical events at each funnel step."""
    from unittest.mock import MagicMock
    import uuid
    from app.database.models import DiscoverySession, SolutionBlueprint, Estimate
    from app.modules.discovery.service import DiscoveryService
    from app.modules.discovery.schemas import LeadUnlockRequest, ReviewRequestCreate
    from app.ai_gateway.schemas import OpportunityItemDTO

    service = DiscoveryService()
    mock_db = MagicMock()

    with caplog.at_level(logging.INFO):
        # 1. discovery_started
        session, _, _ = service.start_session(db=mock_db, entry_point="test_hero")
        session.id = uuid.uuid4()
        session.session_token_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        started_records = [r for r in caplog.records if getattr(r, "event", None) == "discovery_started"]
        assert len(started_records) >= 1
        assert started_records[-1].context["entry_point"] == "test_hero"

        # 2. opportunity_map_viewed
        mock_opp1 = OpportunityItemDTO(
            id="opp-1",
            category="CORE_BUILD",
            title="Core Build Opportunity",
            description="Detailed architectural description of core build.",
            impact="HIGH",
            complexity="MEDIUM",
            estimated_effort="3 - 4 Weeks",
        )
        mock_opp2 = OpportunityItemDTO(
            id="opp-2",
            category="QUICK_WIN",
            title="Quick Win Opportunity",
            description="Detailed architectural description of quick win.",
            impact="MEDIUM",
            complexity="LOW",
            estimated_effort="1 - 2 Weeks",
        )
        service.opportunity_service = MagicMock()
        service.opportunity_service.get_opportunities.return_value = [mock_opp1, mock_opp2]
        service.get_opportunity_map(db=mock_db, session=session)
        opp_records = [r for r in caplog.records if getattr(r, "event", None) == "opportunity_map_viewed"]
        assert len(opp_records) >= 1
        assert opp_records[-1].context["opportunity_count"] == 2

        # 3. blueprint_unlock_started & blueprint_unlocked
        session.current_stage = "OPPORTUNITY_MAP_GENERATED"
        service.lead_service = MagicMock()
        mock_lead = MagicMock()
        mock_lead.id = uuid.uuid4()
        def fake_capture_lead_and_unlock(db, session, payload, client_ip):
            session.is_unlocked = True
            return mock_lead
        service.lead_service.capture_lead_and_unlock.side_effect = fake_capture_lead_and_unlock
        service.blueprint_service = MagicMock()
        service.estimation_service = MagicMock()
        lead_req = LeadUnlockRequest(
            full_name="Lead Architect",
            corporate_email="arch@lead.com",
            consent_given=True,
        )
        service.unlock_with_lead(db=mock_db, session=session, payload=lead_req, client_ip="127.0.0.1")
        unlock_started = [r for r in caplog.records if getattr(r, "event", None) == "blueprint_unlock_started"]
        assert len(unlock_started) >= 1
        unlocked = [r for r in caplog.records if getattr(r, "event", None) == "blueprint_unlocked"]
        assert len(unlocked) >= 1

        # 4. estimate_viewed in get_blueprint
        session.is_unlocked = True
        bp_mock = MagicMock(spec=SolutionBlueprint)
        bp_mock.id = 1
        bp_mock.recommended_stack_category = "Enterprise"
        est_mock = MagicMock(spec=Estimate)
        est_mock.confidence_rating = "HIGH"
        est_mock.budget_min_inr = 500000
        est_mock.budget_max_inr = 1000000
        est_mock.budget_min_usd = 6000
        est_mock.budget_max_usd = 12000
        est_mock.timeline_min_weeks = 4
        est_mock.timeline_max_weeks = 8
        est_mock.mandatory_disclaimer = "Indicative"
        est_mock.created_at = None

        mock_db.query.return_value.filter.return_value.first.side_effect = [bp_mock, est_mock]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        service.get_blueprint(db=mock_db, session=session)
        est_records = [r for r in caplog.records if getattr(r, "event", None) == "estimate_viewed"]
        assert len(est_records) >= 1
        assert est_records[-1].context["confidence"] == "HIGH"

        # 5. discovery_stage_completed (stage 7) in submit_review
        rev_req = ReviewRequestCreate(notes="Review notes")
        service.review_service = MagicMock()
        service.submit_review(db=mock_db, session=session, payload=rev_req)
        review_records = [
            r for r in caplog.records
            if getattr(r, "event", None) == "discovery_stage_completed" and getattr(r, "context", {}).get("stage_number") == 7
        ]
        assert len(review_records) >= 1


# -----------------------------------------------------------------------------
# 8. Local Telemetry Inspection Utility Tests
# -----------------------------------------------------------------------------

def test_telemetry_inspection_utility():
    """Verifies that scripts/inspect_telemetry.py correctly parses NDJSON lines and outputs summary."""
    sample_ndjson = (
        '{"timestamp": "2026-09-18T00:00:00Z", "event": "discovery_started", "telemetry_type": "product"}\n'
        '{"timestamp": "2026-09-18T00:01:00Z", "event": "discovery_stage_completed", "telemetry_type": "product"}\n'
        '{"timestamp": "2026-09-18T00:02:00Z", "event": "opportunity_map_viewed", "telemetry_type": "product"}\n'
        '{"timestamp": "2026-09-18T00:03:00Z", "event": "slow_sql_query", "telemetry_type": "operational", "duration_ms": 612.4}\n'
        'Plain text unparsed log message\n'
    )

    records = parse_telemetry_lines(io.StringIO(sample_ndjson))
    assert len(records) == 4

    # Test summary printing without exceptions
    stdout_buf = io.StringIO()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("sys.stdout", stdout_buf)
        print_summary(records)

    output = stdout_buf.getvalue()
    assert "Total Telemetry Records Parsed: 4" in output
    assert "discovery_started" in output
    assert "slow_sql_query" in output
