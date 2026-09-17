"""
Abstract Protocols & Interfaces for AI Gateway & Providers.
Enforces strict provider-neutral contracts per DOC-ARCH-010.
"""

from typing import Any, Protocol, runtime_checkable
from app.ai_gateway.schemas import ClarificationQuestionsDTO, OpportunityMapDTO


@runtime_checkable
class IAIProvider(Protocol):
    """Low-level adapter protocol for raw provider communication (Mock, LiteLLM, or Direct SDK)."""

    async def complete_structured(
        self,
        prompt: str,
        system_instruction: str,
        target_schema: type,
    ) -> Any:
        """Executes structured completion and returns parsed dictionary or DTO."""
        ...


@runtime_checkable
class IAIServiceGateway(Protocol):
    """High-level application gateway interface consumed by domain services."""

    async def generate_clarifications(
        self, problem_text: str
    ) -> tuple[ClarificationQuestionsDTO, str]:
        """
        Generates 2-5 targeted clarification questions for diagnostic Stage 2.
        Returns: (ClarificationQuestionsDTO, source_provenance_string)
        """
        ...

    async def synthesize_opportunity_map(
        self, problem_text: str, answers: dict[str, str]
    ) -> tuple[OpportunityMapDTO, str]:
        """
        Synthesizes discrete opportunity cards for Stage 4 visualization.
        Returns: (OpportunityMapDTO, source_provenance_string)
        """
        ...
