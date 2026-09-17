"""
Security & Privacy Utilities for [STUDIO_NAME]
Implements pre-transit PII scrubbing, token hashing, and IP anonymization.
"""

import hashlib
import re

# Regex patterns for identifying sensitive user inputs prior to AI gateway transit or storage
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
API_KEY_REGEX = re.compile(r"\b(sk-[a-zA-Z0-9]{20,}|key-[a-zA-Z0-9]{20,}|bearer\s+[a-zA-Z0-9_\-\.]{20,})\b", re.IGNORECASE)
CREDENTIAL_REGEX = re.compile(r"(password|pwd|api_key|secret|conn_str|connectionstring)\s*[:=]\s*[^\s,;]+", re.IGNORECASE)


def scrub_pii(text: str) -> str:
    """
    Sanitizes natural language text by stripping personal identifiers,
    credit cards, API keys, and credentials before transmission to external AI gateways.
    """
    if not text:
        return text

    sanitized = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    sanitized = API_KEY_REGEX.sub("[REDACTED_KEY]", sanitized)
    sanitized = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", sanitized)
    sanitized = SSN_REGEX.sub("[REDACTED_SSN]", sanitized)
    sanitized = PHONE_REGEX.sub("[REDACTED_PHONE]", sanitized)
    sanitized = CREDENTIAL_REGEX.sub(r"\1=[REDACTED_CREDENTIAL]", sanitized)
    return sanitized


def hash_token(token: str) -> str:
    """Computes a SHA-256 digest of a session token for secure database indexing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_ip(ip_address: str) -> str:
    """Produces a deterministic 64-character SHA-256 hash of a client IP address for privacy-compliant audit trails."""
    if not ip_address:
        return "unknown"
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()
