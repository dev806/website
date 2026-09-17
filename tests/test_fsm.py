"""
Unit Tests for the Deterministic 11-State Discovery FSM.
Strictly conforms to DOC-ARCH-011 and DOC-ARCH-003.

Tests:
1. Complete linear valid transition progression through all states.
2. Fallback path transition flow (FALLBACK_ENGAGED).
3. Immediate rejection of illegal/unpermitted transitions with InvalidTransitionError.
4. Terminal state immutability (COMPLETED cannot transition).
5. Guard condition enforcement (unlocked session prerequisites).
6. Non-destructive backtracking routes.
7. Progressive unlock preservation on backtracking.
8. Validation failure recovery (VALIDATION_FAILED -> START).
"""

import uuid
import pytest

from app.database.models import DiscoverySession
from app.modules.discovery.state_machine import (
    DiscoveryState,
    DiscoveryStateMachine,
    InvalidTransitionError,
)


def _create_session(initial_stage: DiscoveryState = DiscoveryState.START, is_unlocked: bool = False) -> DiscoverySession:
    """Helper to create a detached DiscoverySession for pure FSM testing."""
    return DiscoverySession(
        id=uuid.uuid4(),
        session_token_hash=uuid.uuid4().hex,
        current_stage=initial_stage.value,
        is_unlocked=is_unlocked,
    )


def test_linear_happy_path_transitions():
    """Verifies valid linear progression from START through all 11 states to COMPLETED."""
    session = _create_session(DiscoveryState.START)

    # 1. START -> PROBLEM_CAPTURED
    DiscoveryStateMachine.transition(session, DiscoveryState.PROBLEM_CAPTURED)
    assert session.current_stage == DiscoveryState.PROBLEM_CAPTURED.value

    # 2. PROBLEM_CAPTURED -> QUESTIONS_GENERATED
    DiscoveryStateMachine.transition(session, DiscoveryState.QUESTIONS_GENERATED)
    assert session.current_stage == DiscoveryState.QUESTIONS_GENERATED.value

    # 3. QUESTIONS_GENERATED -> QUESTIONS_ANSWERED
    DiscoveryStateMachine.transition(session, DiscoveryState.QUESTIONS_ANSWERED)
    assert session.current_stage == DiscoveryState.QUESTIONS_ANSWERED.value

    # 4. QUESTIONS_ANSWERED -> UNDERSTANDING_GENERATED
    DiscoveryStateMachine.transition(session, DiscoveryState.UNDERSTANDING_GENERATED)
    assert session.current_stage == DiscoveryState.UNDERSTANDING_GENERATED.value

    # 5. UNDERSTANDING_GENERATED -> OPPORTUNITY_MAP_GENERATED
    DiscoveryStateMachine.transition(session, DiscoveryState.OPPORTUNITY_MAP_GENERATED)
    assert session.current_stage == DiscoveryState.OPPORTUNITY_MAP_GENERATED.value

    # 6. OPPORTUNITY_MAP_GENERATED -> BLUEPRINT_REQUESTED
    DiscoveryStateMachine.transition(session, DiscoveryState.BLUEPRINT_REQUESTED)
    assert session.current_stage == DiscoveryState.BLUEPRINT_REQUESTED.value

    # 7. BLUEPRINT_REQUESTED -> LEAD_CAPTURED
    DiscoveryStateMachine.transition(session, DiscoveryState.LEAD_CAPTURED)
    assert session.current_stage == DiscoveryState.LEAD_CAPTURED.value

    # Elevate session unlock status (as done during lead capture)
    session.is_unlocked = True

    # 8. LEAD_CAPTURED -> BLUEPRINT_GENERATED
    DiscoveryStateMachine.transition(session, DiscoveryState.BLUEPRINT_GENERATED)
    assert session.current_stage == DiscoveryState.BLUEPRINT_GENERATED.value

    # 9. BLUEPRINT_GENERATED -> ESTIMATE_GENERATED
    DiscoveryStateMachine.transition(session, DiscoveryState.ESTIMATE_GENERATED)
    assert session.current_stage == DiscoveryState.ESTIMATE_GENERATED.value

    # 10. ESTIMATE_GENERATED -> HUMAN_HANDOFF
    DiscoveryStateMachine.transition(session, DiscoveryState.HUMAN_HANDOFF)
    assert session.current_stage == DiscoveryState.HUMAN_HANDOFF.value

    # 11. HUMAN_HANDOFF -> COMPLETED
    DiscoveryStateMachine.transition(session, DiscoveryState.COMPLETED)
    assert session.current_stage == DiscoveryState.COMPLETED.value


def test_fallback_engaged_path():
    """Verifies fallback activation when external AI provider fails or times out."""
    session = _create_session(DiscoveryState.START)

    DiscoveryStateMachine.transition(session, DiscoveryState.PROBLEM_CAPTURED)
    # AI Gateway timeout/error path -> FALLBACK_ENGAGED
    DiscoveryStateMachine.transition(session, DiscoveryState.FALLBACK_ENGAGED)
    assert session.current_stage == DiscoveryState.FALLBACK_ENGAGED.value

    # User answers heuristic catalog questions -> QUESTIONS_ANSWERED
    DiscoveryStateMachine.transition(session, DiscoveryState.QUESTIONS_ANSWERED)
    assert session.current_stage == DiscoveryState.QUESTIONS_ANSWERED.value


def test_invalid_transitions_rejection():
    """Ensures illegal state transitions raise InvalidTransitionError (HTTP 409)."""
    session = _create_session(DiscoveryState.START)

    # START cannot jump to BLUEPRINT_GENERATED
    with pytest.raises(InvalidTransitionError) as exc_info:
        DiscoveryStateMachine.transition(session, DiscoveryState.BLUEPRINT_GENERATED)
    assert exc_info.value.code == "INVALID_FSM_TRANSITION"
    assert exc_info.value.status_code == 409

    # START cannot jump to ESTIMATE_GENERATED
    with pytest.raises(InvalidTransitionError):
        DiscoveryStateMachine.transition(session, DiscoveryState.ESTIMATE_GENERATED)

    # Transition to PROBLEM_CAPTURED
    DiscoveryStateMachine.transition(session, DiscoveryState.PROBLEM_CAPTURED)

    # PROBLEM_CAPTURED cannot jump to OPPORTUNITY_MAP_GENERATED
    with pytest.raises(InvalidTransitionError):
        DiscoveryStateMachine.transition(session, DiscoveryState.OPPORTUNITY_MAP_GENERATED)


def test_terminal_state_immutability():
    """Verifies that a session in COMPLETED cannot transition to any other state."""
    session = _create_session(DiscoveryState.COMPLETED, is_unlocked=True)

    # Attempt transition from COMPLETED back to START
    with pytest.raises(InvalidTransitionError) as exc_info:
        DiscoveryStateMachine.transition(session, DiscoveryState.START)
    assert "immutable" in exc_info.value.message.lower()

    # Attempt transition from COMPLETED to PROBLEM_CAPTURED
    with pytest.raises(InvalidTransitionError):
        DiscoveryStateMachine.transition(session, DiscoveryState.PROBLEM_CAPTURED)


def test_blueprint_guard_requires_unlocked_session():
    """Verifies that transition to BLUEPRINT_GENERATED is rejected if is_unlocked is False."""
    session = _create_session(DiscoveryState.LEAD_CAPTURED, is_unlocked=False)

    with pytest.raises(InvalidTransitionError) as exc_info:
        DiscoveryStateMachine.transition(session, DiscoveryState.BLUEPRINT_GENERATED)
    assert "unlocked" in exc_info.value.message.lower()


def test_human_handoff_guard_requires_unlocked_session():
    """Verifies that transition to HUMAN_HANDOFF is rejected if is_unlocked is False."""
    session = _create_session(DiscoveryState.ESTIMATE_GENERATED, is_unlocked=False)

    with pytest.raises(InvalidTransitionError) as exc_info:
        DiscoveryStateMachine.transition(session, DiscoveryState.HUMAN_HANDOFF)
    assert "unlocked" in exc_info.value.message.lower()


def test_backtracking_routes():
    """Verifies documented backtracking routes from Stage 4 and Stage 2."""
    session = _create_session(DiscoveryState.OPPORTUNITY_MAP_GENERATED)

    # Backtracking from OPPORTUNITY_MAP_GENERATED to QUESTIONS_ANSWERED
    DiscoveryStateMachine.transition(session, DiscoveryState.QUESTIONS_ANSWERED)
    assert session.current_stage == DiscoveryState.QUESTIONS_ANSWERED.value

    # Backtracking from QUESTIONS_ANSWERED to QUESTIONS_GENERATED
    DiscoveryStateMachine.transition(session, DiscoveryState.QUESTIONS_GENERATED)
    assert session.current_stage == DiscoveryState.QUESTIONS_GENERATED.value

    # Backtracking from QUESTIONS_GENERATED to START
    DiscoveryStateMachine.transition(session, DiscoveryState.START)
    assert session.current_stage == DiscoveryState.START.value


def test_progressive_unlock_preservation_on_backtrack():
    """
    Verifies DOC-ARCH-011 Section 5.2:
    Once is_unlocked is True, user can jump directly from OPPORTUNITY_MAP_GENERATED
    to BLUEPRINT_GENERATED without submitting lead info again.
    """
    session = _create_session(DiscoveryState.OPPORTUNITY_MAP_GENERATED, is_unlocked=True)

    # Allowed because session is unlocked
    assert DiscoveryStateMachine.can_transition(
        session.current_stage,
        DiscoveryState.BLUEPRINT_GENERATED,
        is_unlocked=True,
    ) is True

    DiscoveryStateMachine.transition(session, DiscoveryState.BLUEPRINT_GENERATED)
    assert session.current_stage == DiscoveryState.BLUEPRINT_GENERATED.value


def test_validation_failure_recovery():
    """Verifies that VALIDATION_FAILED can transition back to START or to PROBLEM_CAPTURED."""
    session = _create_session(DiscoveryState.START)

    DiscoveryStateMachine.transition(session, DiscoveryState.VALIDATION_FAILED)
    assert session.current_stage == DiscoveryState.VALIDATION_FAILED.value

    # User re-enters valid input
    DiscoveryStateMachine.transition(session, DiscoveryState.START)
    assert session.current_stage == DiscoveryState.START.value
