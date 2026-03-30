from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class ArchitectureDecision(Base):
    __tablename__ = "architecture_decisions"

    decisionID: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    projectID: Mapped[int] = mapped_column(
        ForeignKey("projects.projectID", ondelete="CASCADE"),
        nullable=False,
    )

    templateID: Mapped[int] = mapped_column(
        ForeignKey("documentation_templates.templateID", ondelete="RESTRICT"),
        nullable=False,
    )

    statusID: Mapped[Optional[int]] = mapped_column(
        ForeignKey("statuses.statusID", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    createdAt: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    lastUpdated: Mapped[datetime] = mapped_column( DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="decisions")
    template: Mapped["DocumentationTemplate"] = relationship("DocumentationTemplate")
    status: Mapped[Optional["Status"]] = relationship("Status")
    fieldValues: Mapped[List["ArchitectureDecisionFieldValue"]] = relationship(
        "ArchitectureDecisionFieldValue",
        back_populates="decision",
        cascade="all, delete-orphan",
    )
    history: Mapped[List["ArchitectureDecisionHistory"]] = relationship(
        "ArchitectureDecisionHistory",
        back_populates="decision",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("title", name="uq_decision_title"),
    )