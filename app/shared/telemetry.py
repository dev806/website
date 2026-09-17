"""
In-House Anonymous Product Telemetry & Operational Event Emitter for [STUDIO_NAME]
Conforms strictly to DOC-ANA-001, DOC-REP-6.2.3-001, and Zero-PII principles.
Emits structured JSON/NDJSON records to stdout via standard Python logging.
Zero database write bloat, zero external analytics SDKs, zero cookies.
"""

import logging
from typing import Any, Optional
from app.shared.logging import correlation_id_ctx
from app.shared.security import scrub_pii

logger = logging.getLogger("app.telemetry")

# Canonical Product Event Taxonomy (Strictly 7 Events)
CANONICAL_PRODUCT_EVENTS = frozenset({
    "discovery_started",
    "discovery_stage_completed",
    "opportunity_map_viewed",
    "blueprint_unlock_started",
    "blueprint_unlocked",
    "estimate_viewed",
    "contact_submitted",
})

# Operational & System Observability Events (Separated from Product Taxonomy)
OPERATIONAL_EVENTS = frozenset({
    "slow_sql_query",
    "slow_http_request",
    "rate_limit_exceeded",
    "ai_completion",
    "ai_fallback",
    "forbidden_access",
    "db_connection_failure",
})

# Keys strictly prohibited from entering the telemetry stream (Data Minimization)
PROHIBITED_PAYLOAD_KEYS = frozenset({
    "name",
    "full_name",
    "first_name",
    "last_name",
    "email",
    "corporate_email",
    "phone",
    "phone_number",
    "password",
    "pwd",
    "secret",
    "secret_key",
    "raw_token",
    "token",
    "prompt",
    "raw_text",
    "clarification_answers",
    "message",
    "credit_card",
    "ssn",
})


def sanitize_telemetry_payload(payload: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Strips prohibited personal identifiers and scrubs natural language strings."""
    if not payload:
        return {}

    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in PROHIBITED_PAYLOAD_KEYS:
            continue
        if isinstance(value, str):
            sanitized[key] = scrub_pii(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_telemetry_payload(value)
        elif isinstance(value, list):
            sanitized[key] = [
                scrub_pii(item) if isinstance(item, str)
                else sanitize_telemetry_payload(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def emit_telemetry_event(
    event_name: str,
    payload: Optional[dict[str, Any]] = None,
    is_operational: bool = False,
    level: int = logging.INFO,
) -> bool:
    """
    Emits an in-house structured telemetry event to the application log stream.
    
    Validates event name against approved taxonomy:
    - Product events must match CANONICAL_PRODUCT_EVENTS.
    - Operational events must match OPERATIONAL_EVENTS.
    
    Enforces zero-PII data minimization.
    Returns True if emitted successfully, False if dropped due to validation.
    """
    if is_operational:
        if event_name not in OPERATIONAL_EVENTS:
            logger.warning(
                f"Dropped unapproved operational telemetry event: {event_name}",
                extra={"event": "telemetry_event_dropped", "dropped_event": event_name},
            )
            return False
    else:
        if event_name not in CANONICAL_PRODUCT_EVENTS:
            logger.warning(
                f"Dropped unapproved product telemetry event: {event_name}",
                extra={"event": "telemetry_event_dropped", "dropped_event": event_name},
            )
            return False

    clean_payload = sanitize_telemetry_payload(payload)
    corr_id = correlation_id_ctx.get()

    logger.log(
        level,
        f"telemetry_event:{event_name}",
        extra={
            "event": event_name,
            "telemetry_type": "operational" if is_operational else "product",
            "context": clean_payload,
            "correlation_id": corr_id,
        },
    )
    return True
