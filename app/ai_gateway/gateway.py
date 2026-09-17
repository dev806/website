"""
AI Service Gateway Orchestrator for [STUDIO_NAME]
Executes pre-transit PII scrubbing, timeout bounding, Pydantic validation, and fallback recovery.
"""

import asyncio
from typing import Optional
from pydantic import ValidationError
from app.ai_gateway.fallback_catalog import (
    get_heuristic_opportunity_map,
    get_heuristic_questions,
)
from app.ai_gateway.interface import IAIProvider, IAIServiceGateway
from app.ai_gateway.mock_provider import MockAIProvider
from app.ai_gateway.schemas import ClarificationQuestionsDTO, OpportunityMapDTO
from app.config import Settings, get_settings
from app.shared.logging import get_logger
from app.shared.security import scrub_pii

logger = get_logger(__name__)


class AIServiceGateway(IAIServiceGateway):
    """
    Production-ready AI Gateway coordinating model requests, telemetry,
    safety sanitization, and deterministic fallback catalogs.
    """

    def __init__(
        self,
        provider: Optional[IAIProvider] = None,
        settings: Optional[Settings] = None,
    ):
        self.settings = settings or get_settings()
        self.provider = provider or MockAIProvider()
        self.timeout = self.settings.ai_timeout_seconds

    async def generate_clarifications(
        self, problem_text: str
    ) -> tuple[ClarificationQuestionsDTO, str]:
        """
        Processes business problem text, scrubs PII, and returns 2-5 clarification questions.
        Falls back seamlessly to deterministic catalog on any failure.
        """
        # Step 1: Pre-transit PII scrubbing
        sanitized_text = scrub_pii(problem_text)

        system_instruction = (
            "You are a Principal Software Architect diagnosing business operational friction. "
            "Generate 2 to 4 high-value clarification questions conforming strictly to the requested schema. "
            "Never fabricate facts or binding commitments."
        )

        try:
            raw_result = await asyncio.wait_for(
                self.provider.complete_structured(
                    prompt=sanitized_text,
                    system_instruction=system_instruction,
                    target_schema=ClarificationQuestionsDTO,
                ),
                timeout=self.timeout,
            )

            # Validate against target schema
            if isinstance(raw_result, ClarificationQuestionsDTO):
                return raw_result, "PROVIDER_LLM"
            if isinstance(raw_result, dict):
                validated = ClarificationQuestionsDTO.model_validate(raw_result)
                return validated, "PROVIDER_LLM"

            raise ValueError(f"Unexpected provider output type: {type(raw_result)}")

        except asyncio.TimeoutError:
            logger.warning("AI Gateway timeout exceeded during clarification generation; engaging fallback catalog")
            return get_heuristic_questions(problem_text), "FALLBACK_TIMEOUT"

        except (ValidationError, ValueError) as val_err:
            logger.warning(f"AI Gateway schema validation error: {val_err}; engaging fallback catalog")
            return get_heuristic_questions(problem_text), "FALLBACK_SCHEMA_ERROR"

        except Exception as exc:
            logger.error(f"AI Gateway upstream provider exception: {exc}; engaging fallback catalog")
            return get_heuristic_questions(problem_text), "FALLBACK_PROVIDER_ERROR"

    async def synthesize_opportunity_map(
        self, problem_text: str, answers: dict[str, str]
    ) -> tuple[OpportunityMapDTO, str]:
        """
        Synthesizes discrete opportunity cards from the problem text and clarification answers.
        Falls back to deterministic studio catalog on failure.
        """
        sanitized_text = scrub_pii(problem_text)
        system_instruction = (
            "You are an Enterprise Systems Architect synthesizing an Executive Opportunity Map. "
            "Group opportunities into Quick Wins, Core Build, Integrations, and System Risks. "
            "Conform strictly to the OpportunityMapDTO schema."
        )

        prompt_payload = f"Problem: {sanitized_text}\nClarification Answers: {answers}"

        try:
            raw_result = await asyncio.wait_for(
                self.provider.complete_structured(
                    prompt=prompt_payload,
                    system_instruction=system_instruction,
                    target_schema=OpportunityMapDTO,
                ),
                timeout=self.timeout,
            )

            if isinstance(raw_result, OpportunityMapDTO):
                return raw_result, "PROVIDER_LLM"
            if isinstance(raw_result, dict):
                validated = OpportunityMapDTO.model_validate(raw_result)
                return validated, "PROVIDER_LLM"

            raise ValueError(f"Unexpected provider output type: {type(raw_result)}")

        except asyncio.TimeoutError:
            logger.warning("AI Gateway timeout exceeded during opportunity map synthesis; engaging fallback catalog")
            return get_heuristic_opportunity_map(problem_text), "FALLBACK_TIMEOUT"

        except (ValidationError, ValueError) as val_err:
            logger.warning(f"AI Gateway schema validation error: {val_err}; engaging fallback catalog")
            return get_heuristic_opportunity_map(problem_text), "FALLBACK_SCHEMA_ERROR"

        except Exception as exc:
            logger.error(f"AI Gateway upstream provider exception: {exc}; engaging fallback catalog")
            return get_heuristic_opportunity_map(problem_text), "FALLBACK_PROVIDER_ERROR"
