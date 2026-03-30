from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.features.user.model import User


class UserRepository:
    @staticmethod
    def get_all(db: Session) -> List[User]:
        stmt = select(User).order_by(User.userID)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(func.lower(User.email) == email.lower()).first()

    @staticmethod
    def create(db: Session, email: str, password_hash: str) -> User:
        user = User(email=email, passwordHash=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User, email: Optional[str], password_hash: Optional[str]) -> User:
        changed = False

        if email is not None and email != user.email:
            user.email = email
            changed = True

        if password_hash is not None:
            user.passwordHash = password_hash
            changed = True

        if changed:
            user.lastUpdated = datetime.utcnow()

        db.commit()
        db.refresh(user)
        return user