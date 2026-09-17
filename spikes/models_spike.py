"""
Spike SP-04: Sample SQLAlchemy 2.0 Declarative Models
Demonstrating UUID / UNIQUEIDENTIFIER, NVARCHAR, and audit timestamps for MSSQL.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
    BigInteger,
    Integer,
)
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, DATETIME2
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DiscoverySessionSpike(Base):
    __tablename__ = "discovery_sessions"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    session_token = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="S01_INITIAL_LANDING")
    created_at = Column(DATETIME2, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DATETIME2, nullable=False, default=lambda: datetime.now(timezone.utc))

    submissions = relationship("ProblemSubmissionSpike", back_populates="session", cascade="all, delete-orphan")

class ProblemSubmissionSpike(Base):
    __tablename__ = "problem_submissions"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    session_id = Column(UNIQUEIDENTIFIER, ForeignKey("discovery_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_problem_text = Column(Text, nullable=False)
    sanitized_problem_text = Column(Text, nullable=False)
    char_count = Column(Integer, nullable=False)
    created_at = Column(DATETIME2, nullable=False, default=lambda: datetime.now(timezone.utc))

    session = relationship("DiscoverySessionSpike", back_populates="submissions")

    __table_args__ = (
        CheckConstraint("char_count >= 20", name="chk_problem_min_length"),
    )

class AuditLogSpike(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    session_id = Column(UNIQUEIDENTIFIER, nullable=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_payload_json = Column(Text, nullable=False)
    ip_hash = Column(String(64), nullable=True)
    created_at = Column(DATETIME2, nullable=False, default=lambda: datetime.now(timezone.utc))
