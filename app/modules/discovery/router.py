"""
FastAPI Route Controllers for the AI Discovery Engine.
Strictly conforms to DOC-ARCH-009 API Contracts and DOC-ARCH-011.

Routes:
- POST /api/v1/discovery/start
- POST /api/v1/discovery/problem
- POST /api/v1/discovery/answers
- GET  /api/v1/discovery/opportunity-map
- POST /api/v1/discovery/lead-unlock
- GET  /api/v1/discovery/blueprint
- POST /api/v1/discovery/review
- GET  /api/v1/discovery/session
"""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database.models import DiscoverySession
from app.database.session import get_db
from app.modules.discovery.schemas import (
    BlueprintResponse,
    LeadUnlockRequest,
    LeadUnlockResponse,
    OpportunityMapResponse,
    ReviewRequestCreate,
    ReviewRequestResponse,
    SessionStateResponse,
    StartSessionData,
    StartSessionRequest,
    StartSessionResponse,
    SubmitAnswersRequest,
    SubmitAnswersResponse,
    SubmitProblemRequest,
    SubmitProblemResponse,
)
from app.modules.discovery.service import DiscoveryService
from app.modules.discovery.session_manager import (
    SESSION_COOKIE_NAME,
    get_current_discovery_session,
)

router = APIRouter(prefix="/api/v1/discovery", tags=["Discovery Engine"])


def get_discovery_service() -> DiscoveryService:
    """Dependency injection for DiscoveryService."""
    return DiscoveryService()


@router.post(
    "/start",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initialize Discovery Session",
    description="Initializes a new diagnostic session, sets an anonymous HTTP-only cookie, and creates root SQL Server record.",
)
def start_discovery_session(
    payload: StartSessionRequest,
    response: Response,
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
    settings: Settings = Depends(get_settings),
):
    session, signed_cookie, raw_token = service.start_session(
        db=db,
        entry_point=payload.entry_point,
        preseed_topic=payload.preseed_topic,
    )

    # Set cryptographic session cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=signed_cookie,
        httponly=True,
        samesite="lax",
        secure=settings.session_secure_cookie,
        max_age=30 * 86400,
    )
    # Also expose token in response headers for automated testing / non-browser clients
    response.headers["X-Session-ID"] = str(session.id)
    response.headers["X-Session-Token"] = raw_token

    return StartSessionResponse(
        success=True,
        data=StartSessionData(
            session_id=session.id,
            stage=session.current_stage,
            is_unlocked=session.is_unlocked,
            created_at=session.created_at,
        ),
    )


@router.post(
    "/problem",
    response_model=SubmitProblemResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Business Problem Text",
    description="Ingests plain-language business friction text, scrubs PII, and returns 2-4 clarification questions.",
)
async def submit_problem(
    payload: SubmitProblemRequest,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    data = await service.submit_problem(
        db=db,
        session=session,
        raw_text=payload.raw_text,
    )
    return SubmitProblemResponse(success=True, data=data)


@router.post(
    "/answers",
    response_model=SubmitAnswersResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Clarification Answers",
    description="Submits selected answers, synthesizes structured understanding and Opportunity Map nodes.",
)
async def submit_answers(
    payload: SubmitAnswersRequest,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    data = await service.submit_answers(
        db=db,
        session=session,
        answers=payload.answers,
    )
    return SubmitAnswersResponse(success=True, data=data)


@router.get(
    "/opportunity-map",
    response_model=OpportunityMapResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Executive Opportunity Map",
    description="Returns the 5-category opportunity matrix (Stage 4 deliverable). 100% Free and Ungated.",
)
def get_opportunity_map(
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    data = service.get_opportunity_map(db=db, session=session)
    return OpportunityMapResponse(success=True, data=data)


@router.post(
    "/lead-unlock",
    response_model=LeadUnlockResponse,
    status_code=status.HTTP_200_OK,
    summary="Progressive Lead Capture & Blueprint Unlock",
    description="Captures corporate email, records compliance consent, elevates session, and generates Blueprint & Estimate.",
)
def unlock_with_lead(
    payload: LeadUnlockRequest,
    request: Request,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    client_ip = request.client.host if request.client else "unknown"
    data = service.unlock_with_lead(
        db=db,
        session=session,
        payload=payload,
        client_ip=client_ip,
    )
    return LeadUnlockResponse(success=True, data=data)


@router.get(
    "/blueprint",
    response_model=BlueprintResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Solution Blueprint & Indicative Estimates",
    description="Returns the 18-section architectural blueprint and confidence-banded planning estimate. Requires unlocked session.",
)
def get_blueprint(
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    data = service.get_blueprint(db=db, session=session)
    return BlueprintResponse(success=True, data=data)


@router.post(
    "/review",
    response_model=ReviewRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request Human Architect Review",
    description="Submits the completed diagnostic to the senior architect triage queue. Transitions FSM to COMPLETED.",
)
def request_architect_review(
    payload: ReviewRequestCreate,
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    data = service.submit_review(
        db=db,
        session=session,
        payload=payload,
    )
    return ReviewRequestResponse(success=True, data=data)


@router.get(
    "/session",
    response_model=SessionStateResponse,
    status_code=status.HTTP_200_OK,
    summary="Inspect Current Discovery Session State",
    description="Returns detailed FSM state, unlock status, and presence of generated artifacts.",
)
def get_session_state(
    session: DiscoverySession = Depends(get_current_discovery_session),
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service),
):
    data = service.get_session_state(db=db, session=session)
    return SessionStateResponse(success=True, data=data)
