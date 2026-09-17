"""
Spike SP-06: AI Gateway Mock Spike
Validates provider-neutral IAIServiceGateway abstraction, Pydantic v2 schema
validation, deterministic fallback behavior, timeout handling, and pre-transit PII scrubbing.
"""
import re
import sys
import os
import asyncio
from typing import Protocol, runtime_checkable, List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError

print("=" * 70)
print("SP-06: AI GATEWAY MOCK & DETERMINISTIC FALLBACK SPIKE")
print("=" * 70)

# 1. PII Scrubber (Pre-Transit Safety)
def scrub_pii(text: str) -> str:
    """Removes sensitive email addresses, phone numbers, and potential card numbers."""
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_CARD]", text)
    return text

# 2. Pydantic v2 Structured Output Schemas
class ClarificationQuestionItem(BaseModel):
    question_id: str
    question_text: str = Field(..., min_length=10)
    category: str
    rationale: str

class DiscoveryClarificationOutput(BaseModel):
    domain: str
    complexity_tier: str
    questions: List[ClarificationQuestionItem]

    @field_validator("questions")
    def validate_question_count(cls, v):
        if len(v) < 3 or len(v) > 5:
            raise ValueError("Discovery requires between 3 and 5 clarification questions.")
        return v

# 3. Deterministic Static Fallback Catalog
STATIC_FALLBACK_QUESTIONS = DiscoveryClarificationOutput(
    domain="General Software Engineering",
    complexity_tier="Medium",
    questions=[
        ClarificationQuestionItem(
            question_id="Q-FALLBACK-01",
            question_text="What are the primary manual steps or bottlenecks in your current operational workflow?",
            category="Workflow",
            rationale="Identifies immediate opportunities for automation."
        ),
        ClarificationQuestionItem(
            question_id="Q-FALLBACK-02",
            question_text="Which third-party software, databases, or APIs need to exchange data with this solution?",
            category="Integrations",
            rationale="Determines integration surface area and technical constraints."
        ),
        ClarificationQuestionItem(
            question_id="Q-FALLBACK-03",
            question_text="Who are the primary end users, and what roles or access tiers will they have?",
            category="User Personas",
            rationale="Determines authorization architecture and usability requirements."
        ),
    ]
)

# 4. Provider-Neutral Protocol
@runtime_checkable
class IAIProvider(Protocol):
    async def complete_structured(self, prompt: str, schema: type) -> dict:
        ...

# 5. Mock Implementations
class MockValidAIProvider:
    async def complete_structured(self, prompt: str, schema: type) -> dict:
        return {
            "domain": "E-Commerce Logistics",
            "complexity_tier": "High",
            "questions": [
                {
                    "question_id": "Q-01",
                    "question_text": "How many orders per day does your warehouse fulfillment pipeline process?",
                    "category": "Scale",
                    "rationale": "Sizes compute and queue requirements."
                },
                {
                    "question_id": "Q-02",
                    "question_text": "Which ERP or inventory system acts as the master source of truth?",
                    "category": "Architecture",
                    "rationale": "Clarifies synchronization boundaries."
                },
                {
                    "question_id": "Q-03",
                    "question_text": "Are dispatch tracking updates expected in real-time or batch intervals?",
                    "category": "Data Flow",
                    "rationale": "Dictates streaming vs polling infrastructure."
                },
            ]
        }

class MockTimeoutAIProvider:
    async def complete_structured(self, prompt: str, schema: type) -> dict:
        await asyncio.sleep(2.0)
        raise TimeoutError("Provider API timeout exceeded (>1000ms)")

class MockMalformedAIProvider:
    async def complete_structured(self, prompt: str, schema: type) -> dict:
        # Returns only 1 question, violating the >= 3 validation rule
        return {
            "domain": "Broken Schema",
            "complexity_tier": "Low",
            "questions": [
                {
                    "question_id": "Q-01",
                    "question_text": "Only one question provided.",
                    "category": "Error",
                    "rationale": "Invalid"
                }
            ]
        }

# 6. Gateway Implementation
class AIServiceGatewaySpike:
    def __init__(self, provider: IAIProvider, timeout_seconds: float = 1.0):
        self.provider = provider
        self.timeout_seconds = timeout_seconds

    async def generate_clarifications(self, raw_problem_text: str) -> tuple[DiscoveryClarificationOutput, str]:
        """
        Processes problem input:
        1. Scrubs PII from input text before transmission.
        2. Dispatches prompt to provider within strict timeout.
        3. Validates output via Pydantic schema.
        4. Triggers deterministic fallback catalog if any step fails.
        """
        sanitized_text = scrub_pii(raw_problem_text)
        try:
            raw_response = await asyncio.wait_for(
                self.provider.complete_structured(sanitized_text, DiscoveryClarificationOutput),
                timeout=self.timeout_seconds
            )
            validated = DiscoveryClarificationOutput.model_validate(raw_response)
            return validated, "PROVIDER_LLM"
        except (TimeoutError, asyncio.TimeoutError):
            print("  --> [GATEWAY NOTICE] Provider timed out. Activating deterministic fallback catalog.")
            return STATIC_FALLBACK_QUESTIONS, "FALLBACK_TIMEOUT"
        except (ValidationError, Exception) as e:
            print(f"  --> [GATEWAY NOTICE] Provider schema failed ({type(e).__name__}). Activating deterministic fallback.")
            return STATIC_FALLBACK_QUESTIONS, "FALLBACK_SCHEMA_ERROR"

# 7. Test Suite
async def run_ai_gateway_tests():
    # Test 1: PII Scrubbing
    input_with_pii = "Our contact is john.doe@enterprise.com and phone is +91-9876543210. Card 4111 2222 3333 4444."
    scrubbed = scrub_pii(input_with_pii)
    assert "john.doe@enterprise.com" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "+91-9876543210" not in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed
    assert "[REDACTED_CARD]" in scrubbed
    print("[PASS] Pre-transit PII scrubber sanitizes sensitive email, phone, and card numbers.")

    # Test 2: Normal Valid Provider
    gw_valid = AIServiceGatewaySpike(MockValidAIProvider())
    out_valid, source = await gw_valid.generate_clarifications("Build custom order management system.")
    assert source == "PROVIDER_LLM"
    assert len(out_valid.questions) == 3
    assert out_valid.domain == "E-Commerce Logistics"
    print(f"[PASS] Valid provider returns Pydantic-validated output ({len(out_valid.questions)} questions).")

    # Test 3: Timeout Fallback
    gw_timeout = AIServiceGatewaySpike(MockTimeoutAIProvider(), timeout_seconds=0.1)
    out_timeout, source_t = await gw_timeout.generate_clarifications("Build custom order management system.")
    assert source_t == "FALLBACK_TIMEOUT"
    assert out_timeout == STATIC_FALLBACK_QUESTIONS
    assert len(out_timeout.questions) == 3
    print("[PASS] Gateway automatically activates deterministic fallback on provider timeout.")

    # Test 4: Malformed Schema Fallback
    gw_malformed = AIServiceGatewaySpike(MockMalformedAIProvider())
    out_malformed, source_m = await gw_malformed.generate_clarifications("Build custom order management system.")
    assert source_m == "FALLBACK_SCHEMA_ERROR"
    assert out_malformed == STATIC_FALLBACK_QUESTIONS
    print("[PASS] Gateway automatically activates deterministic fallback on invalid Pydantic schema.")

if __name__ == "__main__":
    asyncio.run(run_ai_gateway_tests())
    print("\n[PASS] All AI Gateway Mock tests passed successfully.")
    print("=" * 70)
