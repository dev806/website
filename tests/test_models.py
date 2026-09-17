"""
Relational Entity Model Integration Tests for [STUDIO_NAME]
Validates entity persistence, relationships, GUID keys, and constraints on SQL Server.
"""

import uuid
from decimal import Decimal
import pytest
from app.database.models import (
    AuditLog,
    BlueprintSection,
    DiscoverySession,
    Estimate,
    Lead,
    Opportunity,
    ProblemStatement,
    SolutionBlueprint,
    StructuredContext,
)


def test_discovery_session_and_problem_statement(db_session):
    """Verifies creation and relationship between DiscoverySession and ProblemStatement."""
    token_hash = uuid.uuid4().hex

    session = DiscoverySession(
        session_token_hash=token_hash,
        current_stage="START",
        is_unlocked=False,
    )
    db_session.add(session)
    db_session.flush()

    assert session.id is not None
    assert isinstance(session.id, uuid.UUID)

    problem = ProblemStatement(
        session_id=session.id,
        raw_text="Our dispatch team spends 3 hours copying manifests manually.",
        sanitized_text="Our dispatch team spends 3 hours copying manifests manually.",
        character_count=60,
    )
    db_session.add(problem)
    db_session.flush()

    assert problem.id is not None
    assert problem.session.session_token_hash == token_hash
    assert session.problem_statement.character_count == 60


def test_opportunity_and_blueprint_hierarchy(db_session):
    """Verifies Opportunities and SolutionBlueprint with sections."""
    token_hash = uuid.uuid4().hex
    session = DiscoverySession(
        session_token_hash=token_hash,
        current_stage="BLUEPRINT_GENERATED",
    )
    db_session.add(session)
    db_session.flush()

    # Add opportunity
    opp = Opportunity(
        session_id=session.id,
        category="QUICK_WIN",
        title="Automated Manifest Parser",
        description="Extracts data from incoming emails directly into staging tables.",
        business_impact="HIGH",
        technical_complexity="LOW",
        estimated_effort_weeks="2 Weeks",
    )
    db_session.add(opp)

    # Add blueprint
    blueprint = SolutionBlueprint(
        session_id=session.id,
        recommended_stack_category="Python / FastAPI / SQL Server",
        executive_summary="Target state ingestion architecture.",
        status="DRAFT",
    )
    db_session.add(blueprint)
    db_session.flush()

    # Add section
    section = BlueprintSection(
        blueprint_id=blueprint.id,
        section_index=1,
        section_key="executive_summary",
        section_title="Executive Summary",
        content_markdown="Markdown content for section 1",
    )
    db_session.add(section)
    db_session.flush()

    assert len(session.opportunities) == 1
    assert session.solution_blueprint.recommended_stack_category == "Python / FastAPI / SQL Server"
    assert len(session.solution_blueprint.sections) == 1
    assert session.solution_blueprint.sections[0].section_key == "executive_summary"


def test_lead_and_audit_log(db_session):
    """Verifies Lead capture and AuditLog insertion."""
    lead = Lead(
        full_name="Alex Mercer",
        corporate_email="alex@logistics-corp.internal",
        company_name="Logistics Corp",
        lead_status="NEW",
    )
    db_session.add(lead)
    db_session.flush()

    audit = AuditLog(
        event_type="LEAD_GATE_UNLOCKED",
        session_id=None,
        ip_address_hash="abc123hash",
        details_json='{"action": "unlocked"}',
    )
    db_session.add(audit)
    db_session.flush()

    assert lead.id is not None
    assert audit.id is not None
    assert audit.event_type == "LEAD_GATE_UNLOCKED"
