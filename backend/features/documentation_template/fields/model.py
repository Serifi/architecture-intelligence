from __future__ import annotations

from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class DocumentationTemplateField(Base):
    __tablename__ = "documentation_template_fields"

    fieldID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    templateID: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documentation_templates.templateID", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    isRequired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    template: Mapped["DocumentationTemplate"] = relationship(
        "DocumentationTemplate",
        back_populates="fields",
    )