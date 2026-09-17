"""
Human Architect Triage & Review Service for [STUDIO_NAME]
Strictly conforms to DOC-PRD-007, DOC-ARCH-009, and DOC-ARCH-011.

Enforces:
1. Stage 7 Human Architect Bridge queueing (dbo.review_requests).
2. Zero autonomous approvals: AI cannot sign off on architecture, pricing, or SOW.
3. 24-business-hour SLA target commitment.
"""

from sqlalchemy.orm import Session

from app.database.models import DiscoverySession, ReviewRequest
from app.modules.discovery.schemas import ReviewRequestCreate, ReviewRequestData
from app.shared.exceptions import AppException
from app.shared.logging import get_logger

logger = get_logger(__name__)


class ReviewService:
    """
    Manages senior architect triage queueing for unlocked discovery blueprints.
    """

    def submit_review_request(
        self,
        db: Session,
        session: DiscoverySession,
        payload: ReviewRequestCreate,
    ) -> ReviewRequestData:
        """
        Enqueues an architect review ticket in dbo.review_requests.
        Requires session to be unlocked with an associated lead.
        """
        if not session.is_unlocked or not session.lead_id:
            raise AppException(
                code="UNLOCKED_SESSION_REQUIRED",
                message="Submitting a human architect review request requires an unlocked session with contact details.",
                status_code=403,
            )

        logger.info(
            f"Enqueuing senior architect triage ticket for session {session.id}, lead {session.lead_id}"
        )

        review_req = ReviewRequest(
            session_id=session.id,
            lead_id=session.lead_id,
            request_notes=payload.notes.strip() if payload.notes else None,
            status="PENDING",
        )
        db.add(review_req)
        db.flush()

        logger.info(
            f"Review request {review_req.id} created successfully for session {session.id}"
        )

        return ReviewRequestData(
            review_request_id=review_req.id,
            status="PENDING",
            expected_triage_within="1 business day",
        )
