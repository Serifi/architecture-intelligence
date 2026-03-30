from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Status(Base):
    __tablename__ = "statuses"

    statusID: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("position", name="uq_status_position"),
    )