"""
Session Identity & Cryptographic Cookie Management for Discovery.
Strictly conforms to DOC-ARCH-013, DOC-ARCH-014, and DOC-ARCH-021.

Enforces:
1. HMAC-SHA256 cookie signing (studio_session_id).
2. Database hash isolation (session_token_hash stored, raw token never stored).
3. FastAPI dependency injection for session resolution.
"""

import hashlib
import hmac
from typing import Optional
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database.models import DiscoverySession
from app.database.session import get_db
from app.shared.exceptions import AppException
from app.shared.logging import get_logger
from app.shared.security import hash_token

logger = get_logger(__name__)

SESSION_COOKIE_NAME = "studio_session_id"


def sign_token(raw_token: str, secret_key: str) -> str:
    """Signs a token using HMAC-SHA256."""
    sig = hmac.new(
        secret_key.encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{raw_token}.{sig}"


def verify_signed_token(signed_value: str, secret_key: str) -> Optional[str]:
    """Verifies HMAC signature and returns the raw token if valid, else None."""
    if not signed_value or "." not in signed_value:
        return None
    raw_token, signature = signed_value.rsplit(".", 1)
    expected_sig = hmac.new(
        secret_key.encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if hmac.compare_digest(signature, expected_sig):
        return raw_token
    return None


def extract_raw_token(
    request: Request,
    session_cookie: Optional[str] = None,
    x_session_id: Optional[str] = None,
    secret_key: Optional[str] = None,
) -> Optional[str]:
    """
    Extracts raw session token from signed cookie or testing header.
    """
    key = secret_key or ""
    # 1. Check HTTP-only cookie first
    if session_cookie:
        verified = verify_signed_token(session_cookie, key)
        if verified:
            return verified

    # 2. Check X-Session-Token header (signed or raw for API testing)
    header_token = x_session_id or request.headers.get("X-Session-Token") or request.headers.get("X-Session-ID")
    if header_token:
        # If signed header, verify it
        if "." in header_token:
            verified = verify_signed_token(header_token, key)
            if verified:
                return verified
        # Else treat as direct raw token (useful in tests)
        return header_token

    return None


def get_current_discovery_session(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DiscoverySession:
    """
    FastAPI dependency resolving the current active DiscoverySession from
    cookie or header. Raises 401 if missing or invalid.
    """
    session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    raw_token = extract_raw_token(
        request=request,
        session_cookie=session_cookie,
        secret_key=settings.secret_key.get_secret_value(),
    )

    if not raw_token:
        raise AppException(
            code="SESSION_UNAUTHORIZED",
            message="No valid discovery session credentials found in request cookie or header.",
            status_code=401,
        )

    token_hash = hash_token(raw_token)
    session = (
        db.query(DiscoverySession)
        .filter(
            DiscoverySession.session_token_hash == token_hash,
            DiscoverySession.is_deleted == False,
        )
        .first()
    )

    if not session:
        raise AppException(
            code="SESSION_NOT_FOUND",
            message="Discovery session not found or has expired.",
            status_code=404,
        )

    return session
