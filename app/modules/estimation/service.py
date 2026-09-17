"""
Indicative Estimation Engine Service for [STUDIO_NAME]
Strictly conforms to DOC-PRD-006 and DOC-ARCH-003.

Enforces:
1. Zero False Precision (bounded low-to-high planning ranges only).
2. Zero Autonomous Quotations (indicative planning estimates only).
3. Mandatory Non-Binding Legal Disclaimer verbatim from BD-006.
4. Deterministic, parameterized Python calculation.
"""

from decimal import Decimal
import json
import math
from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.database.models import (
    DiscoverySession,
    Estimate,
    Opportunity,
    StructuredContext,
)
from app.modules.discovery.schemas import EstimateDisplayDTO
from app.shared.logging import get_logger

logger = get_logger(__name__)

MANDATORY_DISCLAIMER_TEXT = (
    "IMPORTANT NOTICE: Indicative Planning Range Only. The figures and delivery timelines "
    "presented above are algorithmic planning estimates derived from technical complexity signals. "
    "They do NOT constitute a binding quotation, commercial offer, or contract. Final architecture, "
    "scope ceilings, and legally binding Statements of Work (SOW) strictly require formal review "
    "and authorization by a studio Principal Architect."
)


class EstimationService:
    """
    Algorithmic sizing subsystem calculating confidence-banded indicative budget
    and timeline ranges based on empirical complexity signals.
    """

    def calculate_and_persist(
        self,
        db: Session,
        session: DiscoverySession,
    ) -> Estimate:
        """
        Calculates confidence-banded timeline and investment estimates
        and persists them idempotently to dbo.estimates.
        """
        session_id = session.id
        logger.info(f"Executing algorithmic estimation for discovery session {session_id}")

        context = (
            db.query(StructuredContext)
            .filter(StructuredContext.session_id == session_id)
            .first()
        )
        opps = (
            db.query(Opportunity)
            .filter(Opportunity.session_id == session_id)
            .all()
        )

        complexity_tier = context.complexity_tier.upper() if context else "MEDIUM"
        unknowns_count = 0
        if context and context.flagged_unknowns:
            try:
                parsed_unknowns = json.loads(context.flagged_unknowns)
                unknowns_count = len(parsed_unknowns) if isinstance(parsed_unknowns, list) else 1
            except Exception:
                unknowns_count = 1

        # 1. Base Archetype Effort Units (hours)
        base_effort_hours = 90.0

        # 2. Opportunity Interventions Surcharge
        opp_effort = 0.0
        for opp in opps:
            cat = (opp.category or "").upper()
            if "QUICK_WIN" in cat:
                opp_effort += 15.0
            elif "AUTOMATION" in cat:
                opp_effort += 25.0
            elif "INTEGRATION" in cat:
                opp_effort += 35.0
            elif "CORE_BUILD" in cat:
                opp_effort += 45.0
            elif "SYSTEM_RISK" in cat:
                opp_effort += 20.0
            else:
                opp_effort += 20.0

        # 3. Complexity Tier Multiplier
        if complexity_tier == "LOW":
            tier_multiplier = 0.90
            base_uncertainty = 1.05
        elif complexity_tier == "HIGH":
            tier_multiplier = 1.35
            base_uncertainty = 1.25
        else:  # MEDIUM
            tier_multiplier = 1.10
            base_uncertainty = 1.15

        # 4. Uncertainty Multiplier (Unknowns expand the boundary)
        uncertainty_factor = base_uncertainty + (0.05 * min(unknowns_count, 5))

        total_effort_hours = (base_effort_hours + opp_effort) * tier_multiplier

        # 5. Timeline Band Calculation (DOC-PRD-006 Section 3.1)
        # Sprint Velocity = 35 effort hours per week
        sprint_velocity = 35.0
        min_weeks = max(2, math.ceil((total_effort_hours * 0.85) / sprint_velocity))
        max_weeks = max(min_weeks + 1, math.ceil((total_effort_hours * 1.25 * uncertainty_factor) / sprint_velocity))

        # 6. Budget Band Calculation (DOC-PRD-006 Section 3.2)
        # Parameterized Unit Rates: ₹2,500/hr domestic, $30/hr international
        rate_inr = 2500.0
        rate_usd = 30.0

        budget_min_inr = Decimal(str(round((total_effort_hours * rate_inr * 0.90) / 1000) * 1000))
        budget_max_inr = Decimal(str(round((total_effort_hours * rate_inr * 1.30 * uncertainty_factor) / 1000) * 1000))

        budget_min_usd = Decimal(str(round((total_effort_hours * rate_usd * 0.90) / 100) * 100))
        budget_max_usd = Decimal(str(round((total_effort_hours * rate_usd * 1.30 * uncertainty_factor) / 100) * 100))

        # 7. Confidence Rating
        if uncertainty_factor <= 1.15 and unknowns_count <= 1:
            confidence = "HIGH"
        elif uncertainty_factor <= 1.30:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        sizing_factors = {
            "base_effort_hours": base_effort_hours,
            "opportunity_effort_hours": opp_effort,
            "complexity_tier": complexity_tier,
            "tier_multiplier": tier_multiplier,
            "uncertainty_factor": round(uncertainty_factor, 2),
            "unknowns_count": unknowns_count,
            "total_effort_hours": round(total_effort_hours, 1),
            "sprint_velocity_hours_per_week": sprint_velocity,
        }

        # 8. Idempotent Persistence in dbo.estimates
        estimate = (
            db.query(Estimate)
            .filter(Estimate.session_id == session_id)
            .first()
        )

        if not estimate:
            estimate = Estimate(
                session_id=session_id,
                budget_min_inr=budget_min_inr,
                budget_max_inr=budget_max_inr,
                budget_min_usd=budget_min_usd,
                budget_max_usd=budget_max_usd,
                timeline_min_weeks=min_weeks,
                timeline_max_weeks=max_weeks,
                confidence_rating=confidence,
                sizing_factors_json=json.dumps(sizing_factors),
                mandatory_disclaimer=MANDATORY_DISCLAIMER_TEXT,
            )
            db.add(estimate)
        else:
            estimate.budget_min_inr = budget_min_inr
            estimate.budget_max_inr = budget_max_inr
            estimate.budget_min_usd = budget_min_usd
            estimate.budget_max_usd = budget_max_usd
            estimate.timeline_min_weeks = min_weeks
            estimate.timeline_max_weeks = max_weeks
            estimate.confidence_rating = confidence
            estimate.sizing_factors_json = json.dumps(sizing_factors)
            estimate.mandatory_disclaimer = MANDATORY_DISCLAIMER_TEXT

        db.flush()
        logger.info(
            f"Calculated estimate for session {session_id}: {min_weeks}-{max_weeks} weeks, "
            f"₹{int(budget_min_inr):,}-₹{int(budget_max_inr):,} [confidence={confidence}]"
        )
        return estimate

    @staticmethod
    def format_display_dto(estimate: Estimate) -> EstimateDisplayDTO:
        """Formats the persisted Estimate into display-ready strings."""
        return EstimateDisplayDTO(
            budget_range_inr=f"₹{int(estimate.budget_min_inr):,} – ₹{int(estimate.budget_max_inr):,}",
            budget_range_usd=f"${int(estimate.budget_min_usd):,} – ${int(estimate.budget_max_usd):,}",
            timeline_weeks=f"{estimate.timeline_min_weeks} – {estimate.timeline_max_weeks} Weeks",
            confidence=estimate.confidence_rating,
            mandatory_disclaimer=estimate.mandatory_disclaimer,
        )
