"""
Relational Entity Models for [STUDIO_NAME]
Strictly conforms to DOC-ARCH-006 Relational Entity Canon for Microsoft SQL Server.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mssql import DATETIME2, UNIQUEIDENTIFIER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid


class DiscoverySession(Base, TimestampMixin):
    """Root aggregate tracking the discovery lifecycle from entry to lead gating."""

    __tablename__ = "discovery_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    current_stage: Mapped[str] = mapped_column(
        String(32),
        default="START",
        nullable=False,
    )
    is_unlocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="discovery_sessions")
    problem_statement: Mapped[Optional["ProblemStatement"]] = relationship(
        "ProblemStatement", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    structured_context: Mapped[Optional["StructuredContext"]] = relationship(
        "StructuredContext", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    opportunities: Mapped[list["Opportunity"]] = relationship(
        "Opportunity", back_populates="session", cascade="all, delete-orphan"
    )
    solution_blueprint: Mapped[Optional["SolutionBlueprint"]] = relationship(
        "SolutionBlueprint", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    estimate: Mapped[Optional["Estimate"]] = relationship(
        "Estimate", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    review_requests: Mapped[list["ReviewRequest"]] = relationship(
        "ReviewRequest", back_populates="session", cascade="all, delete-orphan"
    )


class ProblemStatement(Base):
    """User-submitted business problem description and PII-sanitized representation."""

    __tablename__ = "problem_statements"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    sanitized_text: Mapped[str] = mapped_column(Text, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="problem_statement")

    __table_args__ = (
        CheckConstraint("character_count >= 20", name="chk_problem_character_count_min"),
    )


class StructuredContext(Base):
    """Operational synthesis and clarification responses produced by AI discovery."""

    __tablename__ = "structured_contexts"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    clarification_answers: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    core_challenge: Mapped[str] = mapped_column(String(500), nullable=False)
    impacted_workflows: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    flagged_unknowns: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    complexity_tier: Mapped[str] = mapped_column(String(32), nullable=False)  # LOW, MEDIUM, HIGH
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="structured_context")


class Opportunity(Base):
    """Discrete technology or automation opportunity node in the Executive Opportunity Map."""

    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    business_impact: Mapped[str] = mapped_column(String(32), nullable=False)  # HIGH, MEDIUM, LOW
    technical_complexity: Mapped[str] = mapped_column(String(32), nullable=False)  # HIGH, MEDIUM, LOW
    estimated_effort_weeks: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="opportunities")


class SolutionBlueprint(Base, TimestampMixin):
    """Master entity for the 18-section architectural blueprint."""

    __tablename__ = "solution_blueprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    blueprint_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    recommended_stack_category: Mapped[str] = mapped_column(String(128), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False)
    is_architect_endorsed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="solution_blueprint")
    sections: Mapped[list["BlueprintSection"]] = relationship(
        "BlueprintSection", back_populates="blueprint", cascade="all, delete-orphan", order_by="BlueprintSection.section_index"
    )


class BlueprintSection(Base):
    """Individual section of the 18-section Solution Blueprint."""

    __tablename__ = "blueprint_sections"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    blueprint_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("solution_blueprints.id", ondelete="CASCADE"),
        nullable=False,
    )
    section_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_key: Mapped[str] = mapped_column(String(64), nullable=False)
    section_title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    is_human_reviewed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    blueprint: Mapped["SolutionBlueprint"] = relationship("SolutionBlueprint", back_populates="sections")

    __table_args__ = (
        Index("IX_blueprint_sections_index", "blueprint_id", "section_index"),
    )


class Estimate(Base):
    """Algorithmic indicative budget and timeline range calculations."""

    __tablename__ = "estimates"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    budget_min_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    budget_max_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    budget_min_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    budget_max_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    timeline_min_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    timeline_max_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_rating: Mapped[str] = mapped_column(String(32), nullable=False)  # LOW, MEDIUM, HIGH
    sizing_factors_json: Mapped[str] = mapped_column(Text, nullable=False)
    mandatory_disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="estimate")


class Lead(Base):
    """Commercial prospect contact information captured at the blueprint gate."""

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    corporate_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ip_country_code: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    lead_status: Mapped[str] = mapped_column(String(32), default="NEW", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    discovery_sessions: Mapped[list["DiscoverySession"]] = relationship("DiscoverySession", back_populates="lead")
    consents: Mapped[list["LeadConsent"]] = relationship("LeadConsent", back_populates="lead", cascade="all, delete-orphan")
    review_requests: Mapped[list["ReviewRequest"]] = relationship("ReviewRequest", back_populates="lead")


class LeadConsent(Base):
    """Compliance audit record tracking explicit user consent."""

    __tablename__ = "lead_consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
    )
    consent_type: Mapped[str] = mapped_column(String(64), default="BLUEPRINT_DELIVERY", nullable=False)
    consent_text: Mapped[str] = mapped_column(Text, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ip_address_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="consents")


class ReviewRequest(Base):
    """Client request for human architect evaluation of an unlocked blueprint."""

    __tablename__ = "review_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("discovery_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        ForeignKey("leads.id"),
        nullable=False,
    )
    request_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    assigned_architect: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    triaged_at: Mapped[Optional[datetime]] = mapped_column(DATETIME2, nullable=True)

    session: Mapped["DiscoverySession"] = relationship("DiscoverySession", back_populates="review_requests")
    lead: Mapped["Lead"] = relationship("Lead", back_populates="review_requests")


class AuditLog(Base):
    """Append-only audit log for sensitive operational events."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=generate_uuid,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(UNIQUEIDENTIFIER, nullable=True)
    ip_address_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
