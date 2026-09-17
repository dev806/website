"""
Lead Capture & Progressive Unlock Service for [STUDIO_NAME]
Strictly conforms to DOC-PRD-007 and DOC-ARCH-003.

Manages:
1. Contact verification and corporate vs. personal domain classification.
2. Compliance-ready explicit consent recording (dbo.lead_consents).
3. Elevating anonymous discovery sessions (is_unlocked = True).
"""

from sqlalchemy.orm import Session

from app.database.models import DiscoverySession, Lead, LeadConsent
from app.modules.discovery.schemas import LeadUnlockRequest
from app.shared.exceptions import AppException
from app.shared.logging import get_logger
from app.shared.security import hash_ip

logger = get_logger(__name__)

GENERIC_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "aol.com",
    "zoho.com",
    "mail.com",
    "proton.me",
    "protonmail.com",
}


class LeadService:
    """
    Handles Tier 2 contact capture, compliance consent persistence,
    and discovery session elevation.
    """

    def capture_lead_and_unlock(
        self,
        db: Session,
        session: DiscoverySession,
        payload: LeadUnlockRequest,
        client_ip: str,
    ) -> Lead:
        """
        Validates consent, records lead and consent records,
        and unlocks the discovery session.
        """
        if not payload.consent_given:
            raise AppException(
                code="CONSENT_REQUIRED",
                message="Explicit consent is required to process project information and unlock the Solution Blueprint.",
                status_code=422,
            )

        email = str(payload.corporate_email).strip().lower()
        domain = email.split("@")[-1] if "@" in email else ""

        is_corporate = domain not in GENERIC_EMAIL_DOMAINS and "." in domain
        lead_status = "QUALIFIED_CORPORATE" if is_corporate else "NEW"

        logger.info(
            f"Processing lead capture for session {session.id}: email={email}, is_corporate={is_corporate}"
        )

        # Check for existing lead by email to prevent duplication
        lead = db.query(Lead).filter(Lead.corporate_email == email).first()
        if not lead:
            lead = Lead(
                full_name=payload.full_name.strip(),
                corporate_email=email,
                company_name=payload.company_name.strip() if payload.company_name else None,
                phone_number=payload.phone_number.strip() if payload.phone_number else None,
                lead_status=lead_status,
            )
            db.add(lead)
            db.flush()
        else:
            # Update company / phone if provided
            if payload.company_name:
                lead.company_name = payload.company_name.strip()
            if payload.phone_number:
                lead.phone_number = payload.phone_number.strip()
            db.flush()

        # Record explicit consent (DOC-ARCH-006 dbo.lead_consents)
        consent_record = LeadConsent(
            lead_id=lead.id,
            consent_type="BLUEPRINT_DELIVERY",
            consent_text=(
                "I consent to [STUDIO_NAME] processing my project information "
                "to generate architectural blueprints."
            ),
            ip_address_hash=hash_ip(client_ip),
        )
        db.add(consent_record)

        # Elevate session status
        session.lead_id = lead.id
        session.is_unlocked = True
        db.flush()

        logger.info(
            f"Session {session.id} elevated: is_unlocked=True, lead_id={lead.id}"
        )
        return lead
