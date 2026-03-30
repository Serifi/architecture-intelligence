from __future__ import annotations

from typing import Optional, List

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class DocumentationTemplate(Base):
    __tablename__ = "documentation_templates"

    templateID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    fields: Mapped[List["DocumentationTemplateField"]] = relationship(
        "DocumentationTemplateField",
        back_populates="template",
        cascade="all, delete-orphan",
    )