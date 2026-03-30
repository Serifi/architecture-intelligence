from typing import List

from fastapi import APIRouter, Depends, Path, Body, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.user.schema import UserCreate, UserUpdate, UserRead, LoginPayload
from backend.features.user.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    return UserService.list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return UserService.get_user(db, user_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate = Body(...),
    db: Session = Depends(get_db),
):
    return UserService.create_user(db, payload)


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    user_id: int = Path(..., ge=1),
    payload: UserUpdate = Body(...),
    db: Session = Depends(get_db),
):
    return UserService.update_user(db, user_id, payload)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    payload: LoginPayload = Body(...),
    db: Session = Depends(get_db),
):
    return UserService.login(db, payload)