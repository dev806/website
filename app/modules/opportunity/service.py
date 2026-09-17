"""
Executive Opportunity Mapping Service for [STUDIO_NAME]
Strictly conforms to DOC-PRD-004 and DOC-ARCH-003.

Translates operational friction into a 5-category opportunity matrix:
- QUICK_WIN
- CORE_BUILD
- AUTOMATION
- INTEGRATION
- SYSTEM_RISK
"""

from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.ai_gateway.gateway import AIServiceGateway
from app.ai_gateway.schemas import OpportunityItemDTO
from app.database.models import Opportunity
from app.shared.logging import get_logger

logger = get_logger(__name__)


class OpportunityService:
    """
    Coordinates synthesis, ranking, and SQL Server persistence
    of the 100% Free / Ungated Executive Opportunity Map.
    """

    def __init__(self, ai_gateway: Optional[AIServiceGateway] = None):
        self.ai_gateway = ai_gateway or AIServiceGateway()

    async def synthesize_and_persist(
        self,
        db: Session,
        session_id: uuid.UUID,
        problem_text: str,
        answers: dict[str, str],
    ) -> list[OpportunityItemDTO]:
        """
        Synthesizes opportunity nodes via the provider-neutral AI Gateway
        and persists them idempotently to dbo.opportunities.
        """
        logger.info(f"Synthesizing opportunity map for discovery session {session_id}")

        # Ingest problem text and answers via Gateway
        map_dto, source_flag = await self.ai_gateway.synthesize_opportunity_map(
            problem_text=problem_text,
            answers=answers,
        )

        # Clear existing opportunity nodes for this session if re-synthesizing on backtrack
        existing = db.query(Opportunity).filter(Opportunity.session_id == session_id).all()
        for old_opp in existing:
            db.delete(old_opp)
        db.flush()

        # Persist synthesized nodes to dbo.opportunities
        persisted_items: list[OpportunityItemDTO] = []
        for opp in map_dto.opportunities:
            db_opp = Opportunity(
                session_id=session_id,
                category=opp.category,
                title=opp.title,
                description=opp.description,
                business_impact=opp.impact,
                technical_complexity=opp.complexity,
                estimated_effort_weeks=opp.estimated_effort,
            )
            db.add(db_opp)
            persisted_items.append(opp)

        db.flush()
        logger.info(
            f"Persisted {len(persisted_items)} opportunity nodes for session {session_id} [source={source_flag}]"
        )
        return persisted_items

    def get_opportunities(
        self, db: Session, session_id: uuid.UUID
    ) -> list[OpportunityItemDTO]:
        """Loads persisted opportunity cards for a discovery session."""
        db_records = (
            db.query(Opportunity)
            .filter(Opportunity.session_id == session_id)
            .order_by(Opportunity.created_at.asc())
            .all()
        )

        return [
            OpportunityItemDTO(
                id=str(record.id),
                category=record.category,  # type: ignore[arg-type]
                title=record.title,
                description=record.description,
                impact=record.business_impact,  # type: ignore[arg-type]
                complexity=record.technical_complexity,  # type: ignore[arg-type]
                estimated_effort=record.estimated_effort_weeks,
            )
            for record in db_records
        ]
