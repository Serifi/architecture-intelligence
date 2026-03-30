from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class ProjectAttachment(Base):
    __tablename__ = "project_attachments"

    attachmentID: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    projectID: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.projectID", ondelete="CASCADE"), nullable=False
    )

    originalFilename: Mapped[str] = mapped_column(String(255), nullable=False)
    storedFilename: Mapped[str] = mapped_column(String(255), nullable=False)
    mimeType: Mapped[str] = mapped_column(String(100), nullable=False)
    sizeBytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploadedByUserID: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.userID", ondelete="SET NULL"), nullable=True
    )

    createdAt = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project: Mapped["Project"] = relationship("Project", back_populates="attachments")