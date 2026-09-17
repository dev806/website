"""
Pydantic v2 DTOs for AI Gateway Structured Input/Output Validation.
Conforms to DOC-ARCH-009 and DOC-ARCH-010.
"""

from typing import Literal
from pydantic import BaseModel, Field


class QuestionItemDTO(BaseModel):
    """Discrete clarification question node presented to diagnostic users."""

    question_id: str = Field(..., description="Unique slug or identifier for question")
    prompt: str = Field(..., min_length=5, description="Clear, unambiguous clarification question text")
    type: Literal["single_choice", "multiple_choice", "free_text"] = Field(
        default="single_choice", description="Input selection interface format"
    )
    options: list[str] = Field(
        default_factory=list, min_length=2, description="Curated selectable choices"
    )


class ClarificationQuestionsDTO(BaseModel):
    """Root structured container for Stage 2 clarification questions."""

    questions: list[QuestionItemDTO] = Field(
        ..., min_length=2, max_length=5, description="2 to 5 targeted clarification questions"
    )


class OpportunityItemDTO(BaseModel):
    """Discrete opportunity node rendered in the Executive Opportunity Map."""

    id: str = Field(..., description="Deterministic or unique node identifier")
    category: Literal["QUICK_WIN", "CORE_BUILD", "AUTOMATION", "INTEGRATION", "SYSTEM_RISK"] = Field(
        ..., description="Architectural grouping category"
    )
    title: str = Field(..., min_length=5, max_length=255, description="Executive-level opportunity title")
    description: str = Field(..., min_length=10, description="Clear architectural description of the initiative")
    impact: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Business leverage impact")
    complexity: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Engineering and integration complexity")
    estimated_effort: str = Field(..., description="Indicative calendar timeline, e.g. '2 – 3 Weeks'")


class OpportunityMapDTO(BaseModel):
    """Root structured container for Stage 4 Executive Opportunity Map."""

    opportunities: list[OpportunityItemDTO] = Field(
        ..., min_length=1, description="Synthesized opportunity nodes"
    )


class StructuredContextDTO(BaseModel):
    """Operational problem synthesis produced during AI diagnosis."""

    core_challenge: str = Field(..., min_length=10, description="Summarized primary operational friction")
    complexity_tier: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        default="MEDIUM", description="Assessed systems engineering complexity"
    )
    flagged_unknowns: list[str] = Field(
        default_factory=list, description="Unverified dependencies or risks"
    )
    impacted_workflows: list[str] = Field(
        default_factory=list, description="Business workflows impacted by friction"
    )
