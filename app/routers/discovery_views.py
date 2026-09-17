"""
Web Views and HTMX Interaction Controller for the AI Discovery Engine.
Strictly conforms to DOC-PRD-003, DOC-WEB-006, DOC-WEB-007, DOC-WEB-008, and DOC-ARCH-011.

Renders:
1. GET /discovery: Full-page interactive container; resumes existing session or starts new session.
2. POST /discovery/start: Explicit session initialization/reset.
3. POST /discovery/problem: Problem intake, PII scrub, and Stage 2 question delivery.
4. POST /discovery/answers: Clarification intake, Stage 3 synthesis, and Stage 4 Opportunity Map.
5. GET /discovery/stage/opportunity-map: Direct / refresh view of ungated Opportunity Map.
6. POST /discovery/unlock: Tier 2 lead capture, consent record, and Stage 5 & 6 Blueprint reveal.
7. POST /discovery/review: Senior Architect triage submission and Stage 7 handoff confirmation.
8. POST /discovery/backtrack: Non-destructive backtracking preserving progressive unlock.
"""

from typing import Any, Dict, List, Optional
import json
import re
import urllib.parse

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import (
    BlueprintSection,
    DiscoverySession,
    Estimate,
    Opportunity,
    ProblemStatement,
    ReviewRequest,
    SolutionBlueprint,
    StructuredContext,
)
from app.database.session import get_db
from app.modules.discovery.schemas import LeadUnlockRequest, ReviewRequestCreate
from app.modules.discovery.service import DiscoveryService
from app.modules.discovery.session_manager import (
    SESSION_COOKIE_NAME,
    get_current_discovery_session,
    sign_token,
    verify_signed_token,
)
from app.modules.discovery.state_machine import DiscoveryState, DiscoveryStateMachine
from app.shared.exceptions import AppException
from app.shared.logging import get_logger
from app.shared.security import hash_token

logger = get_logger(__name__)

router = APIRouter(prefix="/discovery", tags=["Discovery UX"])
templates = Jinja2Templates(directory="templates")
discovery_service = DiscoveryService()

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _attach_session_cookie(response: Response, signed_cookie: str, secure: bool = False) -> None:
    """Sets standard HTTP-only session cookie."""
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=signed_cookie,
        httponly=True,
        samesite="lax",
        secure=secure,
        max_age=30 * 86400,
    )


async def _parse_form_data(request: Request) -> Dict[str, Any]:
    """Parses form data from application/x-www-form-urlencoded or application/json."""
    content_type = request.headers.get("content-type", "")
    body = await request.body()
    text_body = body.decode("utf-8", errors="replace")
    if "application/json" in content_type:
        try:
            return json.loads(text_body)
        except Exception:
            return {}
    parsed = urllib.parse.parse_qs(text_body, keep_blank_values=True)
    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


def _get_structured_context_data(db: Session, session_id: Any) -> Optional[Dict[str, Any]]:
    """Fetches and formats StructuredContext dictionary for Stage 3 synthesis template."""
    ctx = (
        db.query(StructuredContext)
        .filter(StructuredContext.session_id == session_id)
        .first()
    )
    if not ctx:
        return None
    impacted = []
    if ctx.impacted_workflows:
        try:
            impacted = json.loads(ctx.impacted_workflows)
        except Exception:
            impacted = [ctx.impacted_workflows]
    unknowns = []
    if ctx.flagged_unknowns:
        try:
            unknowns = json.loads(ctx.flagged_unknowns)
        except Exception:
            unknowns = [ctx.flagged_unknowns]
    return {
        "complexity_tier": ctx.complexity_tier,
        "core_challenge": ctx.core_challenge,
        "impacted_workflows": impacted,
        "flagged_unknowns": unknowns,
    }


def _get_or_create_session(
    request: Request, db: Session
) -> tuple[DiscoverySession, Optional[str], bool]:
    """Resolves session from cookie or initializes a new session."""
    settings = get_settings()
    raw_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if raw_cookie:
        token = verify_signed_token(raw_cookie, settings.secret_key.get_secret_value())
        if token:
            token_hash = hash_token(token)
            session = (
                db.query(DiscoverySession)
                .filter(DiscoverySession.session_token_hash == token_hash)
                .first()
            )
            if session:
                return session, None, False

    # Check query param ?session=
    query_session = request.query_params.get("session")
    if query_session:
        session = (
            db.query(DiscoverySession)
            .filter(DiscoverySession.session_token_hash == hash_token(query_session))
            .first()
        )
        if session:
            signed = sign_token(query_session, settings.secret_key.get_secret_value())
            return session, signed, True

    # Create new session
    session, signed_cookie, _ = discovery_service.start_session(db=db, entry_point="web_view")
    return session, signed_cookie, True


@router.get("", response_class=HTMLResponse, summary="Main Discovery Experience")
async def discovery_page_view(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """
    Renders the full-page Discovery container.
    Resumes an active session at its current stage or starts fresh at Stage 1.
    """
    settings = get_settings()
    session, signed_cookie, is_new = _get_or_create_session(request, db)
    current_stage = session.current_stage

    # Stage defaults
    active_stage = "START"
    current_step = 1
    step_percentage = "14%"
    step_title = "Business Problem"

    questions: List[Dict[str, Any]] = []
    opportunities: List[Dict[str, Any]] = []
    structured_ctx_data: Optional[Dict[str, Any]] = None
    blueprint_data: Optional[Dict[str, Any]] = None
    estimate_data: Optional[Dict[str, Any]] = None
    existing_text = ""
    review_request_id = None
    recovery_url = f"{request.base_url}discovery?session={session.id}"

    # Load problem statement if exists
    prob = (
        db.query(ProblemStatement)
        .filter(ProblemStatement.session_id == session.id)
        .first()
    )
    if prob:
        existing_text = prob.sanitized_text

    if current_stage == DiscoveryState.QUESTIONS_GENERATED.value:
        active_stage = "QUESTIONS_GENERATED"
        current_step = 2
        step_percentage = "28%"
        step_title = "Operational Context"
        # Generate or fetch questions
        if prob:
            prob_res = await discovery_service.submit_problem(
                db=db, session=session, raw_text=prob.raw_text
            )
            questions = [q.model_dump() for q in prob_res.questions]

    elif current_stage in (
        DiscoveryState.OPPORTUNITY_MAP_GENERATED.value,
        DiscoveryState.QUESTIONS_ANSWERED.value,
        DiscoveryState.UNDERSTANDING_GENERATED.value,
    ):
        active_stage = "OPPORTUNITY_MAP_GENERATED"
        current_step = 4
        step_percentage = "57%"
        step_title = "Executive Opportunity Map"
        opp_res = discovery_service.get_opportunity_map(db=db, session=session)
        opportunities = [o.model_dump() for o in opp_res.opportunities]
        structured_ctx_data = _get_structured_context_data(db, session.id)

    elif current_stage in (
        DiscoveryState.BLUEPRINT_GENERATED.value,
        DiscoveryState.ESTIMATE_GENERATED.value,
    ):
        if session.is_unlocked:
            active_stage = "BLUEPRINT_GENERATED"
            current_step = 5
            step_percentage = "71%"
            step_title = "Solution Blueprint"
            try:
                bp_res = discovery_service.get_blueprint(db=db, session=session)
                blueprint_data = bp_res.model_dump()
                if bp_res.estimate:
                    estimate_data = bp_res.estimate.model_dump()
            except Exception:
                active_stage = "OPPORTUNITY_MAP_GENERATED"
        else:
            active_stage = "OPPORTUNITY_MAP_GENERATED"
            current_step = 4
            step_percentage = "57%"
            step_title = "Executive Opportunity Map"
            opp_res = discovery_service.get_opportunity_map(db=db, session=session)
            opportunities = [o.model_dump() for o in opp_res.opportunities]
            structured_ctx_data = _get_structured_context_data(db, session.id)

    elif current_stage in (
        DiscoveryState.HUMAN_HANDOFF.value,
        DiscoveryState.COMPLETED.value,
    ):
        active_stage = "COMPLETED"
        current_step = 7
        step_percentage = "100%"
        step_title = "Architect Review Queued"
        rev = (
            db.query(ReviewRequest)
            .filter(ReviewRequest.session_id == session.id)
            .first()
        )
        review_request_id = rev.id if rev else "REV-COMPLETED"

    resp = templates.TemplateResponse(
        request=request,
        name="pages/discovery.html",
        context={
            "page_title": "AI Project Discovery — [STUDIO_NAME]",
            "is_full_page": True,
            "active_stage": active_stage,
            "current_step": current_step,
            "step_percentage": step_percentage,
            "step_title": step_title,
            "existing_text": existing_text,
            "questions": questions,
            "opportunities": opportunities,
            "structured_context": structured_ctx_data,
            "blueprint": blueprint_data,
            "estimate": estimate_data,
            "review_request_id": review_request_id,
            "recovery_url": recovery_url,
        },
    )
    if is_new and signed_cookie:
        _attach_session_cookie(resp, signed_cookie, settings.session_secure_cookie)
    return resp


@router.post("/start", response_class=HTMLResponse, summary="Reset/Start Session")
async def start_session_endpoint(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Explicitly resets or starts a new discovery session and returns Stage 1 partial."""
    settings = get_settings()
    session, signed_cookie, _ = discovery_service.start_session(
        db=db, entry_point="discovery_reset"
    )
    resp = templates.TemplateResponse(
        request=request,
        name="partials/discovery/stage_1_problem.html",
        context={
            "existing_text": "",
            "current_step": 1,
            "step_percentage": "14%",
            "step_title": "Business Problem",
        },
    )
    _attach_session_cookie(resp, signed_cookie, settings.session_secure_cookie)
    return resp


@router.post("/problem", response_class=HTMLResponse, summary="Submit Problem Statement")
async def submit_problem_endpoint(
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Ingests natural language problem, scrubs PII, and returns Stage 2 questions partial."""
    form_data = await _parse_form_data(request)
    raw_text = str(form_data.get("raw_text", ""))
    cleaned_text = raw_text.strip()
    if len(cleaned_text) < 20:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": "Please describe your problem in at least 20 characters so we can understand the operational context.",
                "error_code": "INPUT_TOO_SHORT",
                "retry_stage": "problem",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        result = await discovery_service.submit_problem(
            db=db, session=session, raw_text=cleaned_text
        )
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/stage_2_questions.html",
            context={
                "questions": [q.model_dump() for q in result.questions],
                "current_step": 2,
                "step_percentage": "28%",
                "step_title": "Operational Context",
            },
        )
    except AppException as ae:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": ae.message,
                "error_code": ae.code,
                "retry_stage": "problem",
            },
            status_code=ae.status_code,
        )


@router.post("/answers", response_class=HTMLResponse, summary="Submit Clarifications")
async def submit_answers_endpoint(
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Processes clarification question answers and returns Stage 4 Opportunity Map partial."""
    form_data = await _parse_form_data(request)
    answers: Dict[str, Any] = {}
    for key, value in form_data.items():
        if key not in ("target_stage", "session_id"):
            answers[key] = value

    if not answers:
        answers = {"q1": "General Operations", "q2": "Standard Horizon"}

    try:
        await discovery_service.submit_answers(
            db=db, session=session, answers=answers
        )
        opp_res = discovery_service.get_opportunity_map(db=db, session=session)
        structured_ctx_data = _get_structured_context_data(db, session.id)

        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/stage_4_opportunity_map.html",
            context={
                "opportunities": [o.model_dump() for o in opp_res.opportunities],
                "structured_context": structured_ctx_data,
                "current_step": 4,
                "step_percentage": "57%",
                "step_title": "Executive Opportunity Map",
            },
        )
    except AppException as ae:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": ae.message,
                "error_code": ae.code,
                "retry_stage": "questions",
            },
            status_code=ae.status_code,
        )


@router.get("/stage/opportunity-map", response_class=HTMLResponse, summary="Opportunity Map View")
async def get_opportunity_map_stage(
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Direct refresh/render of the 100% Free and Ungated Opportunity Map."""
    opp_res = discovery_service.get_opportunity_map(db=db, session=session)
    structured_ctx_data = _get_structured_context_data(db, session.id)
    return templates.TemplateResponse(
        request=request,
        name="partials/discovery/stage_4_opportunity_map.html",
        context={
            "opportunities": [o.model_dump() for o in opp_res.opportunities],
            "structured_context": structured_ctx_data,
            "current_step": 4,
            "step_percentage": "57%",
            "step_title": "Executive Opportunity Map",
        },
    )


@router.post("/unlock", response_class=HTMLResponse, summary="Lead Unlock & Reveal Blueprint")
async def unlock_blueprint_endpoint(
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Tier 2 lead capture with consent, unlocking Stage 5 Blueprint and Stage 6 Estimates."""
    form = await _parse_form_data(request)
    full_name = str(form.get("full_name", "")).strip()
    corporate_email = str(form.get("corporate_email", "")).strip()
    company_name = form.get("company_name")
    phone_number = form.get("phone_number")
    consent_val = form.get("consent_given")
    consent_given = consent_val in ("true", "True", "on", "1", True)
    if not consent_given:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": "Explicit consent is required to process project information and unlock the Solution Blueprint.",
                "error_code": "CONSENT_REQUIRED",
                "retry_stage": "opportunity_map",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    clean_email = corporate_email.strip().lower()
    if not EMAIL_REGEX.match(clean_email):
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": "Please enter a valid corporate email address (e.g. name@company.com).",
                "error_code": "INVALID_EMAIL_FORMAT",
                "retry_stage": "opportunity_map",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    client_ip = request.client.host if request.client else "127.0.0.1"
    req_dto = LeadUnlockRequest(
        full_name=full_name.strip(),
        corporate_email=clean_email,
        company_name=company_name.strip() if company_name else None,
        phone_number=phone_number.strip() if phone_number else None,
        consent_given=consent_given,
    )

    try:
        discovery_service.unlock_with_lead(
            db=db, session=session, payload=req_dto, client_ip=client_ip
        )
        bp_res = discovery_service.get_blueprint(db=db, session=session)

        # Concatenate Stage 5 (Blueprint) and Stage 6 (Estimates) in one seamless unlocked view
        bp_html = templates.get_template("partials/discovery/stage_5_blueprint.html").render(
            blueprint=bp_res.model_dump(),
            current_step=5,
            step_percentage="71%",
            step_title="Solution Blueprint",
        )
        est_html = templates.get_template("partials/discovery/stage_6_estimates.html").render(
            estimate=bp_res.estimate.model_dump() if bp_res.estimate else {},
            current_step=6,
            step_percentage="85%",
            step_title="Indicative Estimates",
        )

        combined_html = f"{bp_html}\n{est_html}"
        return HTMLResponse(content=combined_html, status_code=status.HTTP_200_OK)

    except AppException as ae:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": ae.message,
                "error_code": ae.code,
                "retry_stage": "opportunity_map",
            },
            status_code=ae.status_code,
        )


@router.post("/review", response_class=HTMLResponse, summary="Submit Review Handoff")
async def submit_review_endpoint(
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Queues blueprint for Senior Architect triage and returns Stage 7 confirmation."""
    form = await _parse_form_data(request)
    notes_val = form.get("notes")
    notes = str(notes_val).strip() if notes_val else None
    req_dto = ReviewRequestCreate(notes=notes)
    try:
        if session.is_unlocked:
            if session.current_stage == DiscoveryState.OPPORTUNITY_MAP_GENERATED.value:
                DiscoveryStateMachine.transition(
                    session=session,
                    target_state=DiscoveryState.BLUEPRINT_GENERATED,
                    db=db,
                    reason="Progression to Blueprint prior to review handoff.",
                )
            if session.current_stage == DiscoveryState.BLUEPRINT_GENERATED.value:
                DiscoveryStateMachine.transition(
                    session=session,
                    target_state=DiscoveryState.ESTIMATE_GENERATED,
                    db=db,
                    reason="Progression to Estimates prior to review handoff.",
                )

        result = discovery_service.submit_review(
            db=db, session=session, payload=req_dto
        )
        recovery_url = f"{request.base_url}discovery?session={session.id}"

        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/stage_7_handoff.html",
            context={
                "review_request_id": result.review_request_id,
                "recovery_url": recovery_url,
                "current_step": 7,
                "step_percentage": "100%",
                "step_title": "Architect Review Queued",
            },
        )
    except AppException as ae:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": ae.message,
                "error_code": ae.code,
                "retry_stage": "opportunity_map",
            },
            status_code=ae.status_code,
        )


def _backtrack_session(session: DiscoverySession, target_stage: str, db: Session) -> None:
    """Non-destructively steps the FSM backward to the target stage, preserving is_unlocked."""
    current = DiscoveryState(session.current_stage)
    if current == DiscoveryState.COMPLETED:
        raise AppException(
            code="SESSION_COMPLETED",
            message="Completed sessions cannot be modified.",
            status_code=400,
        )

    if target_stage == "opportunity_map":
        if current in (DiscoveryState.ESTIMATE_GENERATED, DiscoveryState.BLUEPRINT_GENERATED):
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.OPPORTUNITY_MAP_GENERATED,
                db=db,
                reason="User backtracked to Opportunity Map",
            )
    elif target_stage == "questions":
        if current in (DiscoveryState.ESTIMATE_GENERATED, DiscoveryState.BLUEPRINT_GENERATED):
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.OPPORTUNITY_MAP_GENERATED,
                db=db,
                reason="User backtracked toward questions",
            )
            current = DiscoveryState(session.current_stage)
        if current == DiscoveryState.OPPORTUNITY_MAP_GENERATED:
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.QUESTIONS_ANSWERED,
                db=db,
                reason="User backtracked toward questions",
            )
            current = DiscoveryState(session.current_stage)
        if current == DiscoveryState.QUESTIONS_ANSWERED:
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.QUESTIONS_GENERATED,
                db=db,
                reason="User backtracked to clarification questions",
            )
    elif target_stage == "problem":
        if current in (DiscoveryState.ESTIMATE_GENERATED, DiscoveryState.BLUEPRINT_GENERATED):
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.OPPORTUNITY_MAP_GENERATED,
                db=db,
                reason="User backtracked toward problem",
            )
            current = DiscoveryState(session.current_stage)
        if current == DiscoveryState.OPPORTUNITY_MAP_GENERATED:
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.QUESTIONS_ANSWERED,
                db=db,
                reason="User backtracked toward problem",
            )
            current = DiscoveryState(session.current_stage)
        if current == DiscoveryState.QUESTIONS_ANSWERED:
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.QUESTIONS_GENERATED,
                db=db,
                reason="User backtracked toward problem",
            )
            current = DiscoveryState(session.current_stage)
        if current == DiscoveryState.QUESTIONS_GENERATED:
            DiscoveryStateMachine.transition(
                session=session,
                target_state=DiscoveryState.START,
                db=db,
                reason="User backtracked to problem statement intake",
            )


@router.post("/backtrack", response_class=HTMLResponse, summary="Non-Destructive Backtrack")
async def backtrack_endpoint(
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """
    Non-destructive backtracking route (POST method).
    Restores earlier stages while strictly preserving progressive unlock status (is_unlocked = True).
    """
    form = await _parse_form_data(request)
    target_stage = str(form.get("target_stage", ""))
    logger.info(
        f"Backtracking session {session.id} to target '{target_stage}'. Current is_unlocked={session.is_unlocked}"
    )

    try:
        if target_stage == "problem":
            prob = (
                db.query(ProblemStatement)
                .filter(ProblemStatement.session_id == session.id)
                .first()
            )
            existing_text = prob.sanitized_text if prob else ""
            _backtrack_session(session, "problem", db)

            return templates.TemplateResponse(
                request=request,
                name="partials/discovery/stage_1_problem.html",
                context={
                    "existing_text": existing_text,
                    "current_step": 1,
                    "step_percentage": "14%",
                    "step_title": "Business Problem",
                },
            )

        elif target_stage == "questions":
            _backtrack_session(session, "questions", db)
            prob = (
                db.query(ProblemStatement)
                .filter(ProblemStatement.session_id == session.id)
                .first()
            )
            questions = []
            if prob:
                questions_dto, _ = await discovery_service.ai_gateway.generate_clarifications(
                    prob.sanitized_text
                )
                questions = [q.model_dump() for q in questions_dto.questions]

            return templates.TemplateResponse(
                request=request,
                name="partials/discovery/stage_2_questions.html",
                context={
                    "questions": questions,
                    "current_step": 2,
                    "step_percentage": "28%",
                    "step_title": "Operational Context",
                },
            )

        elif target_stage == "opportunity_map":
            _backtrack_session(session, "opportunity_map", db)
            opp_res = discovery_service.get_opportunity_map(db=db, session=session)
            structured_ctx_data = _get_structured_context_data(db, session.id)

            return templates.TemplateResponse(
                request=request,
                name="partials/discovery/stage_4_opportunity_map.html",
                context={
                    "opportunities": [o.model_dump() for o in opp_res.opportunities],
                    "structured_context": structured_ctx_data,
                    "current_step": 4,
                    "step_percentage": "57%",
                    "step_title": "Executive Opportunity Map",
                },
            )

        else:
            return templates.TemplateResponse(
                request=request,
                name="partials/discovery/error_partial.html",
                context={
                    "error_message": f"Unknown backtrack target: {target_stage}",
                    "error_code": "INVALID_BACKTRACK_TARGET",
                    "retry_stage": "problem",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    except AppException as ae:
        return templates.TemplateResponse(
            request=request,
            name="partials/discovery/error_partial.html",
            context={
                "error_message": ae.message,
                "error_code": ae.code,
                "retry_stage": "problem",
            },
            status_code=ae.status_code,
        )
