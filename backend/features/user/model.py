from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    userID: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    passwordHash: Mapped[str] = mapped_column(String(255), nullable=False)

    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lastUpdated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )