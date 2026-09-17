"""
SQLAlchemy 2.0 Declarative Base & Persistence Mixins for [STUDIO_NAME]
Conforms to DOC-ARCH-005 and DOC-ARCH-006 for Microsoft SQL Server 2022 Express.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Root declarative base for all persistent entities in [STUDIO_NAME]."""
    pass


class TimestampMixin:
    """Standard audit mixin providing timezone-aware creation and update timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def generate_uuid() -> uuid.UUID:
    """Helper returning a standard random UUID4 value."""
    return uuid.uuid4()
