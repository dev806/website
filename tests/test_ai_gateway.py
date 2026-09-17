"""
AI Gateway Subsystem Integration Tests for [STUDIO_NAME]
"""

import pytest
from app.ai_gateway.fallback_catalog import (
    DEFAULT_FALLBACK_QUESTIONS,
    get_heuristic_opportunity_map,
    get_heuristic_questions,
)
from app.ai_gateway.gateway import AIServiceGateway
from app.ai_gateway.mock_provider import MockAIProvider
from app.shared.security import scrub_pii


def test_pii_scrubbing():
    """Verifies that emails, phones, and credit card patterns are scrubbed."""
    raw_input = (
        "Contact me at founder@startup.io or call +1-555-234-5678. "
        "Card is 4111 2222 3333 4444."
    )
    sanitized = scrub_pii(raw_input)
    assert "founder@startup.io" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_CARD]" in sanitized


@pytest.mark.asyncio
async def test_ai_gateway_valid_generation():
    """Verifies normal mock structured extraction."""
    gateway = AIServiceGateway(MockAIProvider(mode="valid"))
    questions, provenance = await gateway.generate_clarifications(
        "We need to streamline dispatch operations across multiple carriers."
    )
    assert provenance == "PROVIDER_LLM"
    assert len(questions.questions) == 2
    assert questions.questions[0].question_id == "mock_q1"


@pytest.mark.asyncio
async def test_ai_gateway_timeout_fallback():
    """Verifies that timeouts engage the deterministic fallback catalog."""
    gateway = AIServiceGateway(
        MockAIProvider(mode="timeout"),
    )
    gateway.timeout = 0.05
    questions, provenance = await gateway.generate_clarifications(
        "We need to automate manifest entry."
    )
    assert provenance == "FALLBACK_TIMEOUT"
    assert len(questions.questions) >= 2


@pytest.mark.asyncio
async def test_ai_gateway_malformed_schema_fallback():
    """Verifies that schema violations engage the fallback catalog."""
    gateway = AIServiceGateway(MockAIProvider(mode="malformed"))
    questions, provenance = await gateway.generate_clarifications(
        "We need to automate manifest entry."
    )
    assert provenance == "FALLBACK_SCHEMA_ERROR"
    assert len(questions.questions) >= 2


@pytest.mark.asyncio
async def test_ai_gateway_opportunity_map_synthesis():
    """Verifies opportunity map synthesis."""
    gateway = AIServiceGateway(MockAIProvider(mode="valid"))
    opp_map, provenance = await gateway.synthesize_opportunity_map(
        "Manual data entry bottleneck", {"q1": "Spreadsheets"}
    )
    assert provenance == "PROVIDER_LLM"
    assert len(opp_map.opportunities) >= 2
    assert opp_map.opportunities[0].category in ["QUICK_WIN", "CORE_BUILD"]
