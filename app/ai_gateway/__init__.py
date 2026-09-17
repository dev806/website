"""
AI Subsystem & Gateway Package for [STUDIO_NAME]
Provides provider-neutral abstraction, structured output validation, and deterministic fallbacks.
"""

from app.ai_gateway.interface import IAIServiceGateway
from app.ai_gateway.schemas import (
    ClarificationQuestionsDTO,
    OpportunityItemDTO,
    OpportunityMapDTO,
    QuestionItemDTO,
    StructuredContextDTO,
)
from app.ai_gateway.gateway import AIServiceGateway
from app.ai_gateway.mock_provider import MockAIProvider

__all__ = [
    "IAIServiceGateway",
    "AIServiceGateway",
    "MockAIProvider",
    "QuestionItemDTO",
    "ClarificationQuestionsDTO",
    "OpportunityItemDTO",
    "OpportunityMapDTO",
    "StructuredContextDTO",
]
