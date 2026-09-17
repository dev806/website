"""
Deterministic Mock AI Provider for Local Development & Automated Testing.
Enables full offline workflow validation with zero API key dependencies or costs.
"""

import asyncio
from typing import Any
from app.ai_gateway.interface import IAIProvider
from app.ai_gateway.schemas import (
    ClarificationQuestionsDTO,
    OpportunityItemDTO,
    OpportunityMapDTO,
    QuestionItemDTO,
)


class MockAIProvider(IAIProvider):
    """Configurable offline AI provider simulating model responses, latency, and fault modes."""

    def __init__(
        self,
        mode: str = "valid",
        simulated_delay_seconds: float = 0.0,
    ):
        self.mode = mode
        self.simulated_delay_seconds = simulated_delay_seconds

    async def complete_structured(
        self,
        prompt: str,
        system_instruction: str,
        target_schema: type,
    ) -> Any:
        if self.simulated_delay_seconds > 0:
            await asyncio.sleep(self.simulated_delay_seconds)

        if self.mode == "timeout":
            await asyncio.sleep(999.0)

        if self.mode == "error":
            raise RuntimeError("Simulated upstream provider outage (HTTP 500)")

        if self.mode == "malformed":
            return {"malformed_key": "invalid_payload_missing_required_fields"}

        # Return realistic schema-compliant mock objects
        if target_schema == ClarificationQuestionsDTO:
            return ClarificationQuestionsDTO(
                questions=[
                    QuestionItemDTO(
                        question_id="mock_q1",
                        prompt="Which systems are involved in this workflow?",
                        type="single_choice",
                        options=["Custom Web App & SQL", "Spreadsheets & Email", "Enterprise ERP"],
                    ),
                    QuestionItemDTO(
                        question_id="mock_q2",
                        prompt="What is the expected transaction throughput?",
                        type="single_choice",
                        options=["< 100 / day", "100 - 1,000 / day", "> 1,000 / day"],
                    ),
                ]
            )

        if target_schema == OpportunityMapDTO:
            return OpportunityMapDTO(
                opportunities=[
                    OpportunityItemDTO(
                        id="opp_mock_001",
                        category="QUICK_WIN",
                        title="Automated Data Ingestion Bridge",
                        description="Streamlines manual entries using validated API endpoints.",
                        impact="HIGH",
                        complexity="LOW",
                        estimated_effort="2 Weeks",
                    ),
                    OpportunityItemDTO(
                        id="opp_mock_002",
                        category="CORE_BUILD",
                        title="Real-Time Data Orchestrator",
                        description="Centralizes operational state into relational SQL storage.",
                        impact="HIGH",
                        complexity="MEDIUM",
                        estimated_effort="4 Weeks",
                    ),
                ]
            )

        # Generic fallback
        return {}
