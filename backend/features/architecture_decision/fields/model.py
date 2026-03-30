from __future__ import annotations

from sqlalchemy import Integer, Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base
from backend.features.architecture_decision.model import ArchitectureDecision


class ArchitectureDecisionFieldValue(Base):
    __tablename__ = "decision_field_values"

    decisionID: Mapped[int] = mapped_column(
        ForeignKey("architecture_decisions.decisionID", ondelete="CASCADE"),
        nullable=False,
    )

    fieldID: Mapped[int] = mapped_column(
        ForeignKey("documentation_template_fields.fieldID", ondelete="CASCADE"),
        nullable=False,
    )

    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("decisionID", "fieldID", name="pk_architecture_decision_field_value"),
    )

    decision: Mapped["ArchitectureDecision"] = relationship(
        "ArchitectureDecision",
        back_populates="fieldValues",
    )