"""
AI Discovery Deterministic Finite State Machine (11-State FSM)
Strictly conforms to DOC-ARCH-011 and DOC-PRD-003.

Enforces:
1. Zero uncontrolled agent loops (deterministic transitions).
2. Explicit state validation and guard conditions.
3. Persisted state tracking in Microsoft SQL Server (dbo.discovery_sessions).
4. Non-destructive backtracking and progressive unlock preservation.
"""

from enum import Enum
import json
from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import AuditLog, DiscoverySession
from app.shared.exceptions import AppException
from app.shared.logging import get_logger

logger = get_logger(__name__)


class DiscoveryState(str, Enum):
    """
    Authoritative internal FSM states from DOC-ARCH-011.
    Note: 7 user-facing stages are mapped internally across these 11 states + terminal/error states.
    """

    # Stage 1: Problem Input
    START = "START"
    PROBLEM_CAPTURED = "PROBLEM_CAPTURED"

    # Stage 2: Clarification Questions
    QUESTIONS_GENERATED = "QUESTIONS_GENERATED"
    FALLBACK_ENGAGED = "FALLBACK_ENGAGED"
    QUESTIONS_ANSWERED = "QUESTIONS_ANSWERED"

    # Stage 3: Structured Understanding
    UNDERSTANDING_GENERATED = "UNDERSTANDING_GENERATED"

    # Stage 4: Opportunity Map (100% Free / Ungated)
    OPPORTUNITY_MAP_GENERATED = "OPPORTUNITY_MAP_GENERATED"

    # Stage 5: Solution Blueprint + Progressive Lead Gate
    BLUEPRINT_REQUESTED = "BLUEPRINT_REQUESTED"
    LEAD_CAPTURED = "LEAD_CAPTURED"
    BLUEPRINT_GENERATED = "BLUEPRINT_GENERATED"

    # Stage 6: Indicative Estimate
    ESTIMATE_GENERATED = "ESTIMATE_GENERATED"

    # Stage 7: Human Architect Bridge
    HUMAN_HANDOFF = "HUMAN_HANDOFF"
    COMPLETED = "COMPLETED"

    # Error / Transient Recovery State
    VALIDATION_FAILED = "VALIDATION_FAILED"


class InvalidTransitionError(AppException):
    """Raised when an illegal FSM state transition is attempted."""

    def __init__(
        self,
        current_state: str,
        target_state: str,
        reason: Optional[str] = None,
    ):
        msg = f"Cannot transition discovery session from state '{current_state}' to '{target_state}'."
        if reason:
            msg = f"{msg} Reason: {reason}"
        super().__init__(
            code="INVALID_FSM_TRANSITION",
            message=msg,
            status_code=409,
            details=[
                {
                    "current_state": current_state,
                    "target_state": target_state,
                    "reason": reason or "Illegal state transition according to transition matrix.",
                }
            ],
        )


class DiscoveryStateMachine:
    """
    Deterministic State Transition Engine for Discovery Sessions.
    Manages allowed transitions, guard validations, and transition execution.
    """

    # Authoritative Transition Matrix from DOC-ARCH-011 Section 4
    # Maps from_state -> set of allowed target states
    ALLOWED_TRANSITIONS: dict[DiscoveryState, set[DiscoveryState]] = {
        DiscoveryState.START: {
            DiscoveryState.PROBLEM_CAPTURED,
            DiscoveryState.VALIDATION_FAILED,
        },
        DiscoveryState.VALIDATION_FAILED: {
            DiscoveryState.START,
            DiscoveryState.PROBLEM_CAPTURED,
        },
        DiscoveryState.PROBLEM_CAPTURED: {
            DiscoveryState.QUESTIONS_GENERATED,
            DiscoveryState.FALLBACK_ENGAGED,
            DiscoveryState.START,  # Cancel / re-enter
        },
        DiscoveryState.QUESTIONS_GENERATED: {
            DiscoveryState.QUESTIONS_ANSWERED,
            DiscoveryState.START,  # Backtracking to problem input
        },
        DiscoveryState.FALLBACK_ENGAGED: {
            DiscoveryState.QUESTIONS_ANSWERED,
            DiscoveryState.START,  # Backtracking to problem input
        },
        DiscoveryState.QUESTIONS_ANSWERED: {
            DiscoveryState.UNDERSTANDING_GENERATED,
            DiscoveryState.QUESTIONS_GENERATED,  # Backtracking to questions
        },
        DiscoveryState.UNDERSTANDING_GENERATED: {
            DiscoveryState.OPPORTUNITY_MAP_GENERATED,
            DiscoveryState.QUESTIONS_ANSWERED,  # Backtracking to refine answers
        },
        DiscoveryState.OPPORTUNITY_MAP_GENERATED: {
            DiscoveryState.BLUEPRINT_REQUESTED,
            DiscoveryState.QUESTIONS_ANSWERED,  # Backtracking to refine answers
            DiscoveryState.BLUEPRINT_GENERATED,  # Auto-progression if session already unlocked
        },
        DiscoveryState.BLUEPRINT_REQUESTED: {
            DiscoveryState.LEAD_CAPTURED,
            DiscoveryState.OPPORTUNITY_MAP_GENERATED,  # Cancel modal / back
        },
        DiscoveryState.LEAD_CAPTURED: {
            DiscoveryState.BLUEPRINT_GENERATED,
        },
        DiscoveryState.BLUEPRINT_GENERATED: {
            DiscoveryState.ESTIMATE_GENERATED,
            DiscoveryState.OPPORTUNITY_MAP_GENERATED,  # Backtracking
        },
        DiscoveryState.ESTIMATE_GENERATED: {
            DiscoveryState.HUMAN_HANDOFF,
            DiscoveryState.COMPLETED,
            DiscoveryState.OPPORTUNITY_MAP_GENERATED,  # Backtracking
        },
        DiscoveryState.HUMAN_HANDOFF: {
            DiscoveryState.COMPLETED,
        },
        DiscoveryState.COMPLETED: set(),  # Terminal state: session is immutable
    }

    @classmethod
    def can_transition(
        cls,
        from_state: DiscoveryState | str,
        to_state: DiscoveryState | str,
        is_unlocked: bool = False,
    ) -> bool:
        """Determines whether a transition from from_state to to_state is syntactically allowed."""
        try:
            source = DiscoveryState(from_state)
            target = DiscoveryState(to_state)
        except ValueError:
            return False

        allowed = cls.ALLOWED_TRANSITIONS.get(source, set())
        if target in allowed:
            # If target is BLUEPRINT_GENERATED directly from OPPORTUNITY_MAP_GENERATED,
            # session MUST already be unlocked (DOC-ARCH-011 Section 5.2)
            if (
                source == DiscoveryState.OPPORTUNITY_MAP_GENERATED
                and target == DiscoveryState.BLUEPRINT_GENERATED
                and not is_unlocked
            ):
                return False
            return True

        return False

    @classmethod
    def validate_transition(
        cls,
        session: DiscoverySession,
        target_state: DiscoveryState,
    ) -> None:
        """
        Validates whether current session can legally transition to target_state,
        checking transition matrix and domain guard conditions.
        """
        current_state = DiscoveryState(session.current_stage)

        # 1. Terminal state check: completed sessions cannot transition further
        if current_state == DiscoveryState.COMPLETED:
            raise InvalidTransitionError(
                current_state.value,
                target_state.value,
                reason="Discovery session has reached the terminal COMPLETED state and is immutable.",
            )

        # 2. Syntax / Matrix check
        if not cls.can_transition(current_state, target_state, is_unlocked=session.is_unlocked):
            raise InvalidTransitionError(
                current_state.value,
                target_state.value,
                reason=f"Transition from {current_state.value} to {target_state.value} is not in the allowed transition matrix.",
            )

        # 3. Guard conditions for specific states
        if target_state == DiscoveryState.BLUEPRINT_GENERATED:
            if not session.is_unlocked:
                raise InvalidTransitionError(
                    current_state.value,
                    target_state.value,
                    reason="Generating Solution Blueprint requires session to be unlocked via lead capture.",
                )

        if target_state == DiscoveryState.HUMAN_HANDOFF:
            if not session.is_unlocked:
                raise InvalidTransitionError(
                    current_state.value,
                    target_state.value,
                    reason="Requesting human architect review requires an unlocked session with captured contact details.",
                )

    @classmethod
    def transition(
        cls,
        session: DiscoverySession,
        target_state: DiscoveryState,
        db: Optional[Session] = None,
        reason: Optional[str] = None,
        audit_payload: Optional[dict] = None,
    ) -> DiscoveryState:
        """
        Executes a deterministic state transition on the discovery session.
        Validates guards, updates current_stage, records an append-only audit log entry (if db provided),
        and flushes the changes to the session.
        """
        source_state = DiscoveryState(session.current_stage)

        # Validate transition legality
        cls.validate_transition(session, target_state)

        # Apply state update
        session.current_stage = target_state.value

        # Append audit log entry (DOC-ARCH-006 dbo.audit_logs) if db session is provided
        if db is not None:
            audit_details = {
                "from_state": source_state.value,
                "to_state": target_state.value,
                "reason": reason or "FSM transition executed",
                **(audit_payload or {}),
            }

            audit_entry = AuditLog(
                event_type="DISCOVERY_FSM_TRANSITION",
                session_id=session.id,
                details_json=json.dumps(audit_details),
            )
            db.add(audit_entry)
            db.flush()

        logger.info(
            f"FSM transition [session={session.id}]: {source_state.value} -> {target_state.value}"
        )
        return target_state
