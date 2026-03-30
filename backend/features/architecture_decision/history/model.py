from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, DateTime, ForeignKey, Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base
from backend.features.architecture_decision.history.enum import HistoryEventType


class ArchitectureDecisionHistory(Base):
    __tablename__ = "architecture_decision_history"

    historyID: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    decisionID: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("architecture_decisions.decisionID", ondelete="CASCADE"),
        nullable=False,
    )
    userID: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.userID", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fieldID: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("documentation_template_fields.fieldID", ondelete="SET NULL"),
        nullable=True,
    )
    eventType: Mapped[HistoryEventType] = mapped_column(
        SqlEnum(
            HistoryEventType,
            name="history_event_type_enum",
            create_constraint=True,
        ),
        nullable=False,
    )
    createdAt = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    decision: Mapped["ArchitectureDecision"] = relationship(
        "ArchitectureDecision",
        back_populates="history",
    )
    field: Mapped[Optional["DocumentationTemplateField"]] = relationship("DocumentationTemplateField")
    user: Mapped["User"] = relationship("User")