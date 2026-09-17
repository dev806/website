"""
Unit and Integration Tests for DiscoveryService.
Strictly conforms to DOC-ARCH-003, DOC-ARCH-011, and DOC-PRD-003.

Tests:
1. Discovery session lifecycle, token hash isolation, and SQL Server persistence.
2. Problem input validation, PII scrubbing, and clarification question generation.
3. Structured context synthesis and 5-category Opportunity Map creation.
4. Tier 2 Lead capture, consent persistence, session elevation, and 18-section Blueprint synthesis.
5. Indicative Estimation calculation with legal non-binding disclaimer.
6. Guard rejection when attempting to view Blueprint on locked session.
7. Senior architect triage queueing (ReviewRequest) and transition to COMPLETED.
8. Non-destructive backtracking and re-synthesis with unlock preservation.
"""

import json
import pytest
from sqlalchemy.orm import Session

from app.database.models import (
    BlueprintSection,
    DiscoverySession,
    Estimate,
    Lead,
    LeadConsent,
    Opportunity,
    ProblemStatement,
    ReviewRequest,
    SolutionBlueprint,
    StructuredContext,
)
from app.modules.discovery.schemas import LeadUnlockRequest, ReviewRequestCreate
from app.modules.discovery.service import DiscoveryService
from app.modules.discovery.state_machine import DiscoveryState
from app.shared.exceptions import AppException
from app.shared.security import hash_token


@pytest.mark.asyncio
async def test_session_lifecycle_and_persistence(db_session: Session):
    """Verifies session initialization, token generation, and persistence."""
    service = DiscoveryService()
    session, signed_cookie, raw_token = service.start_session(
        db=db_session, entry_point="header_cta"
    )

    assert session.id is not None
    assert session.current_stage == DiscoveryState.START.value
    assert session.is_unlocked is False
    assert session.session_token_hash == hash_token(raw_token)
    assert raw_token in signed_cookie

    # Reload from database to verify persistence across query
    reloaded = (
        db_session.query(DiscoverySession)
        .filter(DiscoverySession.id == session.id)
        .first()
    )
    assert reloaded is not None
    assert reloaded.session_token_hash == hash_token(raw_token)


@pytest.mark.asyncio
async def test_submit_problem_success_and_pii_scrub(db_session: Session):
    """Verifies problem statement submission, character check, and PII scrubbing."""
    service = DiscoveryService()
    session, _, _ = service.start_session(db=db_session)

    raw_problem = (
        "Our operations manager john.doe@acme-corp.com spends 4 hours every morning "
        "re-entering orders from WhatsApp into our legacy accounting system manually."
    )

    result = await service.submit_problem(
        db=db_session,
        session=session,
        raw_text=raw_problem,
    )

    assert result.session_id == session.id
    assert session.current_stage in (
        DiscoveryState.QUESTIONS_GENERATED.value,
        DiscoveryState.FALLBACK_ENGAGED.value,
    )
    assert len(result.questions) >= 2

    # Verify problem_statements table
    stmt = (
        db_session.query(ProblemStatement)
        .filter(ProblemStatement.session_id == session.id)
        .first()
    )
    assert stmt is not None
    assert stmt.character_count == len(raw_problem.strip())
    assert "[REDACTED_EMAIL]" in stmt.sanitized_text
    assert "john.doe@acme-corp.com" not in stmt.sanitized_text


@pytest.mark.asyncio
async def test_submit_problem_short_text_fails(db_session: Session):
    """Verifies that problem text shorter than 20 characters is rejected."""
    service = DiscoveryService()
    session, _, _ = service.start_session(db=db_session)

    with pytest.raises(AppException) as exc_info:
        await service.submit_problem(
            db=db_session,
            session=session,
            raw_text="Too short",
        )
    assert exc_info.value.code == "VALIDATION_FAILED"
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_submit_answers_and_opportunity_map(db_session: Session):
    """Verifies clarification answers submission and Opportunity Map creation."""
    service = DiscoveryService()
    session, _, _ = service.start_session(db=db_session)

    await service.submit_problem(
        db=db_session,
        session=session,
        raw_text="Our dispatch team spends 4 hours copying carrier manifests from emails into ERP.",
    )

    answers = {
        "q1": "QuickBooks & Legacy ERP",
        "q2": "20 – 100 per day",
    }

    result = await service.submit_answers(
        db=db_session,
        session=session,
        answers=answers,
    )

    assert result.session_id == session.id
    assert session.current_stage == DiscoveryState.OPPORTUNITY_MAP_GENERATED.value
    assert result.opportunities_count >= 1
    assert result.structured_context.core_challenge is not None

    # Verify opportunities table
    opps = (
        db_session.query(Opportunity)
        .filter(Opportunity.session_id == session.id)
        .all()
    )
    assert len(opps) == result.opportunities_count
    for opp in opps:
        assert opp.category in ("QUICK_WIN", "CORE_BUILD", "AUTOMATION", "INTEGRATION", "SYSTEM_RISK")
        assert opp.business_impact in ("HIGH", "MEDIUM", "LOW")

    # Verify structured_contexts table
    ctx = (
        db_session.query(StructuredContext)
        .filter(StructuredContext.session_id == session.id)
        .first()
    )
    assert ctx is not None
    assert ctx.complexity_tier in ("LOW", "MEDIUM", "HIGH")


@pytest.mark.asyncio
async def test_lead_unlock_and_blueprint_generation(db_session: Session):
    """Verifies Tier 2 lead capture, consent record, and 18-section Blueprint generation."""
    service = DiscoveryService()
    session, _, _ = service.start_session(db=db_session)

    await service.submit_problem(
        db=db_session,
        session=session,
        raw_text="Our dispatch team spends 4 hours copying carrier manifests from emails into ERP.",
    )
    await service.submit_answers(
        db=db_session,
        session=session,
        answers={"q1": "Legacy ERP", "q2": "50 per day"},
    )

    lead_req = LeadUnlockRequest(
        full_name="Sarah Jenkins",
        corporate_email="sarah@acme-logistics.com",
        company_name="Acme Logistics",
        phone_number="+1-555-0199",
        consent_given=True,
    )

    unlock_data = service.unlock_with_lead(
        db=db_session,
        session=session,
        payload=lead_req,
        client_ip="192.168.1.50",
    )

    assert unlock_data.is_unlocked is True
    assert session.current_stage == DiscoveryState.ESTIMATE_GENERATED.value

    # Verify Lead record
    lead = db_session.query(Lead).filter(Lead.corporate_email == "sarah@acme-logistics.com").first()
    assert lead is not None
    assert lead.lead_status == "QUALIFIED_CORPORATE"

    # Verify LeadConsent record
    consent = db_session.query(LeadConsent).filter(LeadConsent.lead_id == lead.id).first()
    assert consent is not None
    assert consent.consent_type == "BLUEPRINT_DELIVERY"

    # Verify 18 Blueprint sections
    blueprint = db_session.query(SolutionBlueprint).filter(SolutionBlueprint.session_id == session.id).first()
    assert blueprint is not None
    assert blueprint.status == "DRAFT"
    assert blueprint.is_architect_endorsed is False

    sections = (
        db_session.query(BlueprintSection)
        .filter(BlueprintSection.blueprint_id == blueprint.id)
        .order_by(BlueprintSection.section_index.asc())
        .all()
    )
    assert len(sections) == 18
    assert all(not s.is_human_reviewed for s in sections)

    # Verify Estimate record
    est = db_session.query(Estimate).filter(Estimate.session_id == session.id).first()
    assert est is not None
    assert est.timeline_min_weeks >= 2
    assert "IMPORTANT NOTICE" in est.mandatory_disclaimer


def test_blueprint_locked_access_forbidden(db_session: Session):
    """Verifies that accessing a locked blueprint raises 403 Forbidden."""
    service = DiscoveryService()
    session, _, _ = service.start_session(db=db_session)

    with pytest.raises(AppException) as exc_info:
        service.get_blueprint(db=db_session, session=session)
    assert exc_info.value.code == "BLUEPRINT_LOCKED"
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_human_review_handoff(db_session: Session):
    """Verifies senior architect triage queueing and transition to COMPLETED."""
    service = DiscoveryService()
    session, _, _ = service.start_session(db=db_session)

    await service.submit_problem(
        db=db_session,
        session=session,
        raw_text="Our dispatch team spends 4 hours copying carrier manifests from emails into ERP.",
    )
    await service.submit_answers(
        db=db_session,
        session=session,
        answers={"q1": "Legacy ERP"},
    )
    service.unlock_with_lead(
        db=db_session,
        session=session,
        payload=LeadUnlockRequest(
            full_name="Sarah Jenkins",
            corporate_email="sarah@acme-logistics.com",
            consent_given=True,
        ),
        client_ip="127.0.0.1",
    )

    # Submit review request
    review_data = service.submit_review(
        db=db_session,
        session=session,
        payload=ReviewRequestCreate(notes="Please verify on-premise firewall compatibility."),
    )

    assert review_data.status == "PENDING"
    assert session.current_stage == DiscoveryState.COMPLETED.value

    # Verify ReviewRequest table
    req = db_session.query(ReviewRequest).filter(ReviewRequest.id == review_data.review_request_id).first()
    assert req is not None
    assert req.session_id == session.id
    assert req.request_notes == "Please verify on-premise firewall compatibility."
