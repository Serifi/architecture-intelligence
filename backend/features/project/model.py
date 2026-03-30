from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Text, DateTime, Enum as SqlEnum, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base
from backend.features.project.enum import PriorityLevel


class Project(Base):
    __tablename__ = "projects"

    projectID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    userID: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.userID", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    priority: Mapped[PriorityLevel] = mapped_column(
        SqlEnum(PriorityLevel, name="priority_enum", create_constraint=True),
        nullable=False,
        default=PriorityLevel.MEDIUM,
    )

    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    icon: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)

    creationDate: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    lastUpdated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    decisions: Mapped[List["ArchitectureDecision"]] = relationship(
        "ArchitectureDecision",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    attachments: Mapped[List["ProjectAttachment"]] = relationship(
        "ProjectAttachment",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    user: Mapped["User"] = relationship("User", back_populates="projects")

    __table_args__ = (
        UniqueConstraint("userID", "position", name="uq_project_user_position"),
    )