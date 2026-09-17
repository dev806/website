"""
Pydantic Request & Response DTOs for Discovery API Endpoints.
Conforms strictly to DOC-ARCH-009 API Contracts and DOC-ARCH-011.
"""

from datetime import datetime
from typing import Optional
import re
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ai_gateway.schemas import OpportunityItemDTO, QuestionItemDTO

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# -----------------------------------------------------------------------------
# Endpoint 01: POST /api/v1/discovery/start
# -----------------------------------------------------------------------------
class StartSessionRequest(BaseModel):
    """Payload for initiating a new discovery session."""

    entry_point: str = Field(
        default="homepage_hero",
        description="Source tracking identifier for discovery entry",
    )
    preseed_topic: Optional[str] = Field(
        default=None,
        description="Optional seed topic or pillar from marketing pages",
    )


class StartSessionData(BaseModel):
    session_id: uuid.UUID
    stage: str
    is_unlocked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StartSessionResponse(BaseModel):
    success: bool = True
    data: StartSessionData


# -----------------------------------------------------------------------------
# Endpoint 02: POST /api/v1/discovery/problem
# -----------------------------------------------------------------------------
class SubmitProblemRequest(BaseModel):
    """Plain-language business friction intake."""

    raw_text: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Client business problem description (minimum 20 characters)",
    )


class SubmitProblemData(BaseModel):
    session_id: uuid.UUID
    stage: str
    character_count: int
    questions: list[QuestionItemDTO]


class SubmitProblemResponse(BaseModel):
    success: bool = True
    data: SubmitProblemData


# -----------------------------------------------------------------------------
# Endpoint 03: POST /api/v1/discovery/answers
# -----------------------------------------------------------------------------
class SubmitAnswersRequest(BaseModel):
    """User selections for clarification questions."""

    answers: dict[str, str] = Field(
        ...,
        min_length=1,
        description="Dictionary mapping question_id to selected answer value",
    )


class StructuredContextSummaryDTO(BaseModel):
    core_challenge: str
    complexity_tier: str
    flagged_unknowns: list[str] = Field(default_factory=list)


class SubmitAnswersData(BaseModel):
    session_id: uuid.UUID
    stage: str
    structured_context: StructuredContextSummaryDTO
    opportunities_count: int


class SubmitAnswersResponse(BaseModel):
    success: bool = True
    data: SubmitAnswersData


# -----------------------------------------------------------------------------
# Endpoint 04: GET /api/v1/discovery/opportunity-map
# -----------------------------------------------------------------------------
class OpportunityMapData(BaseModel):
    session_id: uuid.UUID
    opportunities: list[OpportunityItemDTO]


class OpportunityMapResponse(BaseModel):
    success: bool = True
    data: OpportunityMapData


# -----------------------------------------------------------------------------
# Endpoint 05: POST /api/v1/discovery/lead-unlock
# -----------------------------------------------------------------------------
class LeadUnlockRequest(BaseModel):
    """Tier 2 progressive lead capture input."""

    full_name: str = Field(..., min_length=2, max_length=255)
    corporate_email: str = Field(..., min_length=5, description="Corporate or business work email")
    company_name: Optional[str] = Field(default=None, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=64)
    consent_given: bool = Field(
        ...,
        description="Explicit consent flag (must be True to unlock blueprint)",
    )

    @field_validator("corporate_email")
    @classmethod
    def validate_corporate_email(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if not EMAIL_PATTERN.match(v_clean):
            raise ValueError("Invalid email format.")
        return v_clean


class LeadUnlockData(BaseModel):
    session_id: uuid.UUID
    is_unlocked: bool
    lead_id: uuid.UUID
    message: str = "Solution Blueprint unlocked successfully."


class LeadUnlockResponse(BaseModel):
    success: bool = True
    data: LeadUnlockData


# -----------------------------------------------------------------------------
# Endpoint 06: GET /api/v1/discovery/blueprint
# -----------------------------------------------------------------------------
class BlueprintSectionDisplayDTO(BaseModel):
    index: int
    title: str
    content: str
    is_human_reviewed: bool = False


class EstimateDisplayDTO(BaseModel):
    budget_range_inr: str
    budget_range_usd: str
    timeline_weeks: str
    confidence: str
    mandatory_disclaimer: str


class BlueprintData(BaseModel):
    session_id: uuid.UUID
    status_badge: str = "AI_GENERATED_PRELIMINARY_DRAFT"
    recommended_stack: str
    sections: list[BlueprintSectionDisplayDTO]
    estimate: EstimateDisplayDTO


class BlueprintResponse(BaseModel):
    success: bool = True
    data: BlueprintData


# -----------------------------------------------------------------------------
# Endpoint 07: POST /api/v1/discovery/review
# -----------------------------------------------------------------------------
class ReviewRequestCreate(BaseModel):
    """Submission payload for senior architect triage queue."""

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional client notes, questions, or specific technical constraints",
    )


class ReviewRequestData(BaseModel):
    review_request_id: uuid.UUID
    status: str = "PENDING"
    expected_triage_within: str = "1 business day"


class ReviewRequestResponse(BaseModel):
    success: bool = True
    data: ReviewRequestData


# -----------------------------------------------------------------------------
# Endpoint 08: GET /api/v1/discovery/session (Session State Lookup)
# -----------------------------------------------------------------------------
class SessionStateData(BaseModel):
    session_id: uuid.UUID
    current_stage: str
    is_unlocked: bool
    has_problem: bool
    has_answers: bool
    has_opportunities: bool
    has_blueprint: bool
    has_estimate: bool
    created_at: datetime
    updated_at: datetime


class SessionStateResponse(BaseModel):
    success: bool = True
    data: SessionStateData
