"""
Discovery Engine Coordinator Service for [STUDIO_NAME]
Strictly conforms to DOC-ARCH-003, DOC-ARCH-011, and DOC-PRD-003.

Coordinates:
1. Deterministic 11-state FSM lifecycle and state transitions.
2. Provider-neutral AI Gateway integration with PII scrubbing and fallback catalogs.
3. Subsystem orchestration (Opportunity Map, Solution Blueprint, Estimation, Leads, Review).
4. Persisted session continuity in Microsoft SQL Server.
"""

import json
from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.ai_gateway.gateway import AIServiceGateway
from app.config import Settings, get_settings
from app.database.models import (
    BlueprintSection,
    DiscoverySession,
    Estimate,
    Opportunity,
    ProblemStatement,
    SolutionBlueprint,
    StructuredContext,
)
from app.modules.blueprint.service import BlueprintService
from app.modules.discovery.schemas import (
    BlueprintData,
    BlueprintSectionDisplayDTO,
    LeadUnlockData,
    LeadUnlockRequest,
    OpportunityMapData,
    ReviewRequestCreate,
    ReviewRequestData,
    SessionStateData,
    StructuredContextSummaryDTO,
    SubmitAnswersData,
    SubmitProblemData,
)
from app.modules.discovery.session_manager import sign_token
from app.modules.discovery.state_machine import DiscoveryState, DiscoveryStateMachine
from app.modules.estimation.service import EstimationService
from app.modules.leads.service import LeadService
from app.modules.opportunity.service import OpportunityService
from app.modules.review.service import ReviewService
from app.shared.exceptions import AppException
from app.shared.logging import get_logger
from app.shared.security import hash_token, scrub_pii

logger = get_logger(__name__)


class DiscoveryService:
    """
    Central coordinator orchestrating the 7 user-facing consultative discovery stages
    using the internal 11-state deterministic state machine.
    """

    def __init__(
        self,
        ai_gateway: Optional[AIServiceGateway] = None,
        opportunity_service: Optional[OpportunityService] = None,
        blueprint_service: Optional[BlueprintService] = None,
        estimation_service: Optional[EstimationService] = None,
        lead_service: Optional[LeadService] = None,
        review_service: Optional[ReviewService] = None,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or get_settings()
        self.ai_gateway = ai_gateway or AIServiceGateway()
        self.opportunity_service = opportunity_service or OpportunityService(self.ai_gateway)
        self.blueprint_service = blueprint_service or BlueprintService()
        self.estimation_service = estimation_service or EstimationService()
        self.lead_service = lead_service or LeadService()
        self.review_service = review_service or ReviewService()

    def start_session(
        self,
        db: Session,
        entry_point: str = "homepage_hero",
        preseed_topic: Optional[str] = None,
    ) -> tuple[DiscoverySession, str, str]:
        """
        Endpoint 01: Initializes a new diagnostic session in SQL Server,
        generates signed HMAC session cookie token, and sets state to START.
        Returns: (session, signed_cookie, raw_token)
        """
        raw_token = str(uuid.uuid4())
        token_hash = hash_token(raw_token)
        signed_cookie = sign_token(raw_token, self.settings.secret_key.get_secret_value())

        session = DiscoverySession(
            session_token_hash=token_hash,
            current_stage=DiscoveryState.START.value,
            is_unlocked=False,
            is_deleted=False,
        )
        db.add(session)
        db.flush()

        logger.info(
            f"Initialized new discovery session {session.id} [entry_point={entry_point}]"
        )
        return session, signed_cookie, raw_token

    async def submit_problem(
        self,
        db: Session,
        session: DiscoverySession,
        raw_text: str,
    ) -> SubmitProblemData:
        """
        Endpoint 02: Receives business problem text, validates character count (>= 20),
        scrubs PII, transitions state to PROBLEM_CAPTURED, queries AI Gateway for clarification
        questions, and transitions to QUESTIONS_GENERATED (or FALLBACK_ENGAGED).
        """
        clean_text = raw_text.strip()
        if len(clean_text) < 20:
            # Revert or record validation failure in FSM if needed
            if DiscoveryStateMachine.can_transition(session.current_stage, DiscoveryState.VALIDATION_FAILED):
                DiscoveryStateMachine.transition(
                    session=session,
                    target_state=DiscoveryState.VALIDATION_FAILED,
                    db=db,
                    reason="Problem text is shorter than 20 characters.",
                )
            raise AppException(
                code="VALIDATION_FAILED",
                message="Problem description must be at least 20 characters long.",
                status_code=422,
                details=[{"field": "raw_text", "issue": "Minimum length is 20 characters."}],
            )

        # Transition FSM: -> PROBLEM_CAPTURED
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.PROBLEM_CAPTURED,
            db=db,
            reason="User submitted valid problem text.",
        )

        # Pre-transit PII scrubbing
        sanitized = scrub_pii(clean_text)

        # Persist / update ProblemStatement in dbo.problem_statements
        stmt = db.query(ProblemStatement).filter(ProblemStatement.session_id == session.id).first()
        if not stmt:
            stmt = ProblemStatement(
                session_id=session.id,
                raw_text=clean_text,
                sanitized_text=sanitized,
                character_count=len(clean_text),
            )
            db.add(stmt)
        else:
            stmt.raw_text = clean_text
            stmt.sanitized_text = sanitized
            stmt.character_count = len(clean_text)
        db.flush()

        # Query AI Gateway for 2-4 clarification questions
        questions_dto, source_flag = await self.ai_gateway.generate_clarifications(sanitized)

        # Determine target state based on gateway resolution
        target_state = (
            DiscoveryState.FALLBACK_ENGAGED
            if source_flag.startswith("FALLBACK_")
            else DiscoveryState.QUESTIONS_GENERATED
        )

        DiscoveryStateMachine.transition(
            session=session,
            target_state=target_state,
            db=db,
            reason=f"Clarification questions generated via {source_flag}.",
        )

        return SubmitProblemData(
            session_id=session.id,
            stage=session.current_stage,
            character_count=len(clean_text),
            questions=questions_dto.questions,
        )

    async def submit_answers(
        self,
        db: Session,
        session: DiscoverySession,
        answers: dict[str, str],
    ) -> SubmitAnswersData:
        """
        Endpoint 03: Submits multiple-choice answers, validates them,
        synthesizes structured problem context, generates the Opportunity Map,
        and auto-synthesizes Blueprint/Estimate if session was already unlocked.
        """
        if not answers:
            raise AppException(
                code="VALIDATION_FAILED",
                message="At least one question answer must be provided.",
                status_code=422,
            )

        # FSM Transition: -> QUESTIONS_ANSWERED
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.QUESTIONS_ANSWERED,
            db=db,
            reason="User submitted clarification answers.",
        )

        # Fetch problem statement
        problem = db.query(ProblemStatement).filter(ProblemStatement.session_id == session.id).first()
        problem_text = problem.sanitized_text if problem else "Business operational friction"

        # Synthesize Structured Context
        core_challenge = self._derive_core_challenge(problem_text, answers)
        complexity_tier = self._assess_complexity_tier(problem_text, answers)
        flagged_unknowns = self._identify_unknowns(answers)
        impacted_workflows = ["Operational data entry", "Cross-system synchronization"]

        # Persist or update StructuredContext in dbo.structured_contexts
        ctx = db.query(StructuredContext).filter(StructuredContext.session_id == session.id).first()
        if not ctx:
            ctx = StructuredContext(
                session_id=session.id,
                clarification_answers=json.dumps(answers),
                core_challenge=core_challenge,
                impacted_workflows=json.dumps(impacted_workflows),
                flagged_unknowns=json.dumps(flagged_unknowns),
                complexity_tier=complexity_tier,
            )
            db.add(ctx)
        else:
            ctx.clarification_answers = json.dumps(answers)
            ctx.core_challenge = core_challenge
            ctx.impacted_workflows = json.dumps(impacted_workflows)
            ctx.flagged_unknowns = json.dumps(flagged_unknowns)
            ctx.complexity_tier = complexity_tier
        db.flush()

        # FSM Transition: -> UNDERSTANDING_GENERATED
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.UNDERSTANDING_GENERATED,
            db=db,
            reason="Structured operational challenge context synthesized.",
        )

        # Synthesize & Persist Opportunity Map Nodes (dbo.opportunities)
        opp_nodes = await self.opportunity_service.synthesize_and_persist(
            db=db,
            session_id=session.id,
            problem_text=problem_text,
            answers=answers,
        )

        # FSM Transition: -> OPPORTUNITY_MAP_GENERATED (100% Free / Ungated)
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.OPPORTUNITY_MAP_GENERATED,
            db=db,
            reason="Free ungated Opportunity Map generated.",
        )

        # Backtracking Support: If session is already unlocked, re-synthesize Blueprint & Estimate
        if session.is_unlocked:
            logger.info(
                f"Session {session.id} is already unlocked; automatically re-synthesizing downstream Blueprint & Estimate"
            )
            self.blueprint_service.generate_draft_blueprint(db=db, session=session)
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.BLUEPRINT_GENERATED,
                db=db,
                reason="Idempotent blueprint re-synthesis on refined answers.",
            )
            self.estimation_service.calculate_and_persist(db=db, session=session)
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.ESTIMATE_GENERATED,
                db=db,
                reason="Idempotent estimate re-calculation on refined answers.",
            )

        return SubmitAnswersData(
            session_id=session.id,
            stage=session.current_stage,
            structured_context=StructuredContextSummaryDTO(
                core_challenge=core_challenge,
                complexity_tier=complexity_tier,
                flagged_unknowns=flagged_unknowns,
            ),
            opportunities_count=len(opp_nodes),
        )

    def get_opportunity_map(
        self,
        db: Session,
        session: DiscoverySession,
    ) -> OpportunityMapData:
        """
        Endpoint 04: Retrieves the generated Opportunity Map cards (Stage 4).
        100% Free & Ungated.
        """
        opps = self.opportunity_service.get_opportunities(db=db, session_id=session.id)
        return OpportunityMapData(
            session_id=session.id,
            opportunities=opps,
        )

    def unlock_with_lead(
        self,
        db: Session,
        session: DiscoverySession,
        payload: LeadUnlockRequest,
        client_ip: str,
    ) -> LeadUnlockData:
        """
        Endpoint 05: Captures corporate email and name, records explicit consent,
        elevates session status (is_unlocked = True), and triggers full Solution
        Blueprint and Indicative Estimate synthesis.
        """
        # FSM Transition: -> BLUEPRINT_REQUESTED
        if session.current_stage == DiscoveryState.OPPORTUNITY_MAP_GENERATED.value:
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.BLUEPRINT_REQUESTED,
                db=db,
                reason="User initiated blueprint progressive lead gate.",
            )

        # Capture Lead & Record Consent
        lead = self.lead_service.capture_lead_and_unlock(
            db=db,
            session=session,
            payload=payload,
            client_ip=client_ip,
        )

        # FSM Transition: -> LEAD_CAPTURED
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.LEAD_CAPTURED,
            db=db,
            reason="Contact details and legal consent successfully recorded.",
        )

        # Synthesize 18-Section Solution Blueprint Draft
        self.blueprint_service.generate_draft_blueprint(db=db, session=session)
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.BLUEPRINT_GENERATED,
            db=db,
            reason="18-section architectural blueprint draft created.",
        )

        # Synthesize Indicative Estimate
        self.estimation_service.calculate_and_persist(db=db, session=session)
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.ESTIMATE_GENERATED,
            db=db,
            reason="Confidence-banded indicative planning estimate calculated.",
        )

        return LeadUnlockData(
            session_id=session.id,
            is_unlocked=session.is_unlocked,
            lead_id=lead.id,
            message="Solution Blueprint unlocked successfully.",
        )

    def get_blueprint(
        self,
        db: Session,
        session: DiscoverySession,
    ) -> BlueprintData:
        """
        Endpoint 06: Retrieves the full 18-section Solution Blueprint and
        indicative planning estimates. Requires session to be unlocked.
        """
        if not session.is_unlocked:
            raise AppException(
                code="BLUEPRINT_LOCKED",
                message="Solution Blueprint is locked. Progressive contact unlock required.",
                status_code=403,
            )

        blueprint = (
            db.query(SolutionBlueprint)
            .filter(SolutionBlueprint.session_id == session.id)
            .first()
        )
        if not blueprint:
            raise AppException(
                code="BLUEPRINT_NOT_FOUND",
                message="Solution Blueprint has not yet been generated for this session.",
                status_code=404,
            )

        sections = (
            db.query(BlueprintSection)
            .filter(BlueprintSection.blueprint_id == blueprint.id)
            .order_by(BlueprintSection.section_index.asc())
            .all()
        )

        estimate = (
            db.query(Estimate)
            .filter(Estimate.session_id == session.id)
            .first()
        )
        if not estimate:
            # Fallback calculate if missing
            estimate = self.estimation_service.calculate_and_persist(db=db, session=session)

        estimate_dto = EstimationService.format_display_dto(estimate)

        section_dtos = [
            BlueprintSectionDisplayDTO(
                index=s.section_index,
                title=s.section_title,
                content=s.content_markdown,
                is_human_reviewed=s.is_human_reviewed,
            )
            for s in sections
        ]

        return BlueprintData(
            session_id=session.id,
            status_badge="AI_GENERATED_PRELIMINARY_DRAFT",
            recommended_stack=blueprint.recommended_stack_category,
            sections=section_dtos,
            estimate=estimate_dto,
        )

    def submit_review(
        self,
        db: Session,
        session: DiscoverySession,
        payload: ReviewRequestCreate,
    ) -> ReviewRequestData:
        """
        Endpoint 07: Submits the diagnostic to the senior architect triage queue.
        Transitions state to HUMAN_HANDOFF and then COMPLETED.
        """
        # FSM Transition: -> HUMAN_HANDOFF
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.HUMAN_HANDOFF,
            db=db,
            reason="User requested human architect evaluation.",
        )

        review_data = self.review_service.submit_review_request(
            db=db,
            session=session,
            payload=payload,
        )

        # FSM Transition: -> COMPLETED (Terminal State)
        DiscoveryStateMachine.transition(
            session=session,
            target_state=DiscoveryState.COMPLETED,
            db=db,
            reason="Review ticket enqueued; session marked completed.",
        )

        return review_data

    def get_session_state(
        self,
        db: Session,
        session: DiscoverySession,
    ) -> SessionStateData:
        """Endpoint 08: Returns comprehensive inspection of session status and associated artifacts."""
        has_problem = (
            db.query(ProblemStatement).filter(ProblemStatement.session_id == session.id).count() > 0
        )
        has_answers = (
            db.query(StructuredContext).filter(StructuredContext.session_id == session.id).count() > 0
        )
        has_opportunities = (
            db.query(Opportunity).filter(Opportunity.session_id == session.id).count() > 0
        )
        has_blueprint = (
            db.query(SolutionBlueprint).filter(SolutionBlueprint.session_id == session.id).count() > 0
        )
        has_estimate = (
            db.query(Estimate).filter(Estimate.session_id == session.id).count() > 0
        )

        return SessionStateData(
            session_id=session.id,
            current_stage=session.current_stage,
            is_unlocked=session.is_unlocked,
            has_problem=has_problem,
            has_answers=has_answers,
            has_opportunities=has_opportunities,
            has_blueprint=has_blueprint,
            has_estimate=has_estimate,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    # -------------------------------------------------------------------------
    # Internal Heuristic Derivation Helpers
    # -------------------------------------------------------------------------
    def _derive_core_challenge(self, problem_text: str, answers: dict[str, str]) -> str:
        """Derives a concise operational problem summary."""
        lower = problem_text.lower()
        if "invoice" in lower or "accounting" in lower:
            return "Manual reconciliation and cross-system data entry between sales channels and accounting ledgers."
        if "lead" in lower or "customer" in lower or "crm" in lower:
            return "Fragmented customer intake and delayed operational response times across communication tools."
        if "dispatch" in lower or "shipping" in lower or "logistics" in lower:
            return "Manual logistics manifest transcription resulting in dispatch delays and shipping errors."
        return "Operational data bottlenecks caused by manual cross-system transcription."

    def _assess_complexity_tier(self, problem_text: str, answers: dict[str, str]) -> str:
        """Assesses system engineering complexity tier (LOW, MEDIUM, HIGH)."""
        answers_str = " ".join(str(v).lower() for v in answers.values())
        combined = f"{problem_text.lower()} {answers_str}"

        if "high volume" in combined or "legacy" in combined or "erp" in combined or "custom database" in combined:
            return "HIGH"
        if "spreadsheets" in combined or "quickbooks" in combined or "moderate volume" in combined:
            return "MEDIUM"
        return "LOW"

    def _identify_unknowns(self, answers: dict[str, str]) -> list[str]:
        """Identifies architectural unknowns based on answers."""
        unknowns = []
        for val in answers.values():
            val_lower = str(val).lower()
            if "legacy" in val_lower:
                unknowns.append("Legacy application database export formats and API availability.")
            if "security" in val_lower or "firewall" in val_lower:
                unknowns.append("On-premise firewall traversal and inbound webhook connectivity.")
        if not unknowns:
            unknowns.append("Third-party API rate limits and export schema stability.")
        return unknowns
