from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.features.user.repository import UserRepository
from backend.features.user.schema import UserCreate, UserUpdate, LoginPayload


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def list_users(db: Session):
        return UserRepository.get_all(db)

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    @staticmethod
    def create_user(db: Session, payload: UserCreate):
        existing = UserRepository.get_by_email(db, payload.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User '{payload.email}' cannot be created: email already exists.",
            )

        password_hash = pwd_context.hash(payload.password)

        user = UserRepository.create(
            db=db,
            email=payload.email,
            password_hash=password_hash,
        )

        return {
            "message": f"User '{user.email}' was created successfully.",
            "user": user,
        }

    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserUpdate):
        user = UserService.get_user(db, user_id)

        if payload.email is None and payload.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update payload must contain at least one field.",
            )

        if payload.email is not None and payload.email.lower() != user.email.lower():
            existing = UserRepository.get_by_email(db, payload.email)
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User '{payload.email}' cannot be updated: email already exists.",
                )

        password_hash = None
        if payload.password is not None:
            password_hash = pwd_context.hash(payload.password)

        updated = UserRepository.update(
            db=db,
            user=user,
            email=payload.email,
            password_hash=password_hash,
        )

        return {
            "message": f"User '{updated.email}' was updated successfully.",
            "user": updated,
        }

    @staticmethod
    def login(db: Session, payload: LoginPayload):
        user = UserRepository.get_by_email(db, payload.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist.",
            )

        if not pwd_context.verify(payload.password, user.passwordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect.",
            )

        return {
            "message": f"Login successful for user '{user.email}'.",
            "user": user,
        }