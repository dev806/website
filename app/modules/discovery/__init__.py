"""
Discovery Engine Module for [STUDIO_NAME]
Implements the 11-State Deterministic FSM and consultative diagnostics.
Conforms to DOC-ARCH-011 and DOC-PRD-003.
"""

from app.modules.discovery.state_machine import DiscoveryState, DiscoveryStateMachine

__all__ = ["DiscoveryState", "DiscoveryStateMachine"]
