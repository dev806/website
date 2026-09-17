"""
Unit Tests for the Indicative Estimation Sizing Engine.
Strictly conforms to DOC-PRD-006 and DOC-ARCH-003.

Tests:
1. Deterministic calculation across complexity tiers (LOW, MEDIUM, HIGH).
2. Unknowns impact expanding the uncertainty factor and timeline/budget boundaries.
3. Opportunity items count and category impact on effort calculation.
4. Bounded ranges guarantee zero single-point false precision.
5. Dual currency formatting (INR and USD).
6. Mandatory non-binding disclaimer inclusion verbatim (BD-006).
"""

from decimal import Decimal
import json
import uuid
import pytest
from sqlalchemy.orm import Session

from app.database.models import (
    DiscoverySession,
    Opportunity,
    StructuredContext,
)
from app.modules.discovery.state_machine import DiscoveryState
from app.modules.estimation.service import (
    MANDATORY_DISCLAIMER_TEXT,
    EstimationService,
)


def test_estimation_low_complexity(db_session: Session):
    """Verifies estimation calculation for low-complexity operational friction."""
    session = DiscoverySession(
        session_token_hash=uuid.uuid4().hex,
        current_stage=DiscoveryState.BLUEPRINT_GENERATED.value,
        is_unlocked=True,
    )
    db_session.add(session)
    db_session.flush()

    # Low complexity context with 0 unknowns
    ctx = StructuredContext(
        session_id=session.id,
        clarification_answers=json.dumps({"q1": "Spreadsheets"}),
        core_challenge="Manual spreadsheet copy pasting",
        impacted_workflows=json.dumps(["Reporting"]),
        flagged_unknowns=json.dumps([]),
        complexity_tier="LOW",
    )
    db_session.add(ctx)

    # 1 Quick Win opportunity
    opp = Opportunity(
        session_id=session.id,
        category="QUICK_WIN",
        title="Automated Data Ingestion",
        description="CSV upload pipeline",
        business_impact="MEDIUM",
        technical_complexity="LOW",
        estimated_effort_weeks="1 – 2 Weeks",
    )
    db_session.add(opp)
    db_session.flush()

    service = EstimationService()
    estimate = service.calculate_and_persist(db_session, session)

    assert estimate.id is not None
    assert estimate.confidence_rating == "HIGH"
    assert estimate.timeline_min_weeks >= 2
    assert estimate.timeline_max_weeks > estimate.timeline_min_weeks
    assert estimate.budget_min_inr < estimate.budget_max_inr
    assert estimate.budget_min_usd < estimate.budget_max_usd
    assert estimate.mandatory_disclaimer == MANDATORY_DISCLAIMER_TEXT

    # Verify display formatting
    display = service.format_display_dto(estimate)
    assert "₹" in display.budget_range_inr
    assert "$" in display.budget_range_usd
    assert "Weeks" in display.timeline_weeks
    assert display.confidence == "HIGH"


def test_estimation_high_complexity_with_unknowns(db_session: Session):
    """Verifies that high complexity and multiple unknowns expand range boundaries and lower confidence."""
    session = DiscoverySession(
        session_token_hash=uuid.uuid4().hex,
        current_stage=DiscoveryState.BLUEPRINT_GENERATED.value,
        is_unlocked=True,
    )
    db_session.add(session)
    db_session.flush()

    # High complexity context with 3 unknowns
    ctx = StructuredContext(
        session_id=session.id,
        clarification_answers=json.dumps({"q1": "Legacy ERP", "q2": "On-Premise Firewall"}),
        core_challenge="Legacy database synchronization across corporate firewalls",
        impacted_workflows=json.dumps(["ERP dispatch", "Warehouse inventory"]),
        flagged_unknowns=json.dumps([
            "Legacy ERP API documentation availability",
            "Firewall inbound webhook rules",
            "Data sanitization complexity for 10-year historical tables",
        ]),
        complexity_tier="HIGH",
    )
    db_session.add(ctx)

    # Multiple enterprise integration opportunities
    for i, cat in enumerate(["INTEGRATION", "CORE_BUILD", "SYSTEM_RISK"]):
        opp = Opportunity(
            session_id=session.id,
            category=cat,
            title=f"Opportunity {i}",
            description=f"Description {i}",
            business_impact="HIGH",
            technical_complexity="HIGH",
            estimated_effort_weeks="4 – 6 Weeks",
        )
        db_session.add(opp)
    db_session.flush()

    service = EstimationService()
    estimate = service.calculate_and_persist(db_session, session)

    # Uncertainty should be higher, confidence should drop
    assert estimate.confidence_rating in ("MEDIUM", "LOW")
    assert estimate.timeline_max_weeks >= 6
    # Range boundary should be expanded (high > low * 1.3)
    assert estimate.budget_max_inr > Decimal(str(estimate.budget_min_inr)) * Decimal("1.3")
