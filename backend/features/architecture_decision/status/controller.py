from typing import List

from fastapi import APIRouter, Depends, Path, Body, status as http_status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.architecture_decision.status.schema import (
    StatusRead,
    StatusCreate,
    StatusUpdate,
    StatusResponse,
    DeleteResponse,
    StatusReorderItem,
    StatusReorderResponse,
)
from backend.features.architecture_decision.status.service import StatusService

router = APIRouter(prefix="/statuses", tags=["statuses"])


@router.get("/", response_model=List[StatusRead])
def list_statuses(db: Session = Depends(get_db)):
    return StatusService.list_statuses(db)


@router.put("/reorder", response_model=StatusReorderResponse)
def reorder_statuses(
    payload: List[StatusReorderItem] = Body(...),
    db: Session = Depends(get_db),
):
    return StatusService.reorder_statuses(db, payload)


@router.get("/{status_id}", response_model=StatusRead)
def get_status(
    status_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return StatusService.get_status(db, status_id)


@router.post("/", response_model=StatusResponse, status_code=http_status.HTTP_201_CREATED)
def create_status(
    payload: StatusCreate = Body(...),
    db: Session = Depends(get_db),
):
    return StatusService.create_status(db, payload)


@router.put("/{status_id}", response_model=StatusResponse)
def update_status(
    status_id: int = Path(..., ge=1),
    payload: StatusUpdate = Body(...),
    db: Session = Depends(get_db),
):
    return StatusService.update_status(db, status_id, payload)


@router.delete("/{status_id}", response_model=DeleteResponse, status_code=http_status.HTTP_200_OK)
def delete_status(
    status_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return StatusService.delete_status(db, status_id)