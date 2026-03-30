from typing import List

from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session
from sqlalchemy import func  # NEU

from backend.features.architecture_decision.status.model import Status  # NEU
from backend.features.architecture_decision.status.repository import StatusRepository
from backend.features.architecture_decision.status.schema import (
    StatusCreate,
    StatusUpdate,
    StatusReorderItem,
)


class StatusService:
    @staticmethod
    def list_statuses(db: Session):
        return StatusRepository.get_all(db)

    @staticmethod
    def get_status(db: Session, status_id: int):
        status_obj = StatusRepository.get_by_id(db, status_id)
        if status_obj is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Status not found.",
            )
        return status_obj

    @staticmethod
    def create_status(db: Session, payload: StatusCreate):
        if StatusRepository.exists_by_name(db, payload.name):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Status '{payload.name}' cannot be created: name already exists.",
            )

        max_pos = db.query(func.max(Status.position)).scalar() or 0

        if payload.position is None:
            new_position = max_pos + 1
        else:
            new_position = payload.position

            if new_position < 0:
                new_position = 0

            if new_position > max_pos + 1:
                new_position = max_pos + 1

            StatusRepository.shift_positions_from(db, new_position)

        status_obj = StatusRepository.create(
            db,
            name=payload.name,
            color=payload.color,
            position=new_position,
        )

        return {
            "message": f"Status '{status_obj.name}' was created successfully.",
            "status": status_obj,
        }

    @staticmethod
    def update_status(db: Session, status_id: int, payload: StatusUpdate):
        status_obj = StatusService.get_status(db, status_id)

        if (
            payload.name is None
            and payload.color is None
            and payload.position is None
        ):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Update payload must contain at least one field.",
            )

        new_name = payload.name if payload.name is not None else status_obj.name
        new_color = payload.color if payload.color is not None else status_obj.color
        new_position = payload.position if payload.position is not None else status_obj.position

        if new_name is None or new_color is None or new_position is None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="All fields (name, color, position) are required.",
            )

        if StatusRepository.exists_by_name(db, new_name, exclude_id=status_id):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Status '{new_name}' cannot be updated: name already exists.",
            )

        updated = StatusRepository.update(
            db,
            status=status_obj,
            name=payload.name,
            color=payload.color,
            position=payload.position,
        )

        return {
            "message": f"Status '{updated.name}' was updated successfully.",
            "status": updated,
        }

    @staticmethod
    def delete_status(db: Session, status_id: int):
        status_obj = StatusService.get_status(db, status_id)
        StatusRepository.delete(db, status_obj)
        return {
            "message": f"Status '{status_obj.name}' was deleted successfully.",
            "deleted": True,
        }

    @staticmethod
    def reorder_statuses(db: Session, items: List[StatusReorderItem]):
        if not items:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Reorder payload must not be empty.",
            )

        ids = [i.statusID for i in items]
        positions = [i.position for i in items]

        if len(set(ids)) != len(ids):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Duplicate status IDs in reorder payload.",
            )

        if len(set(positions)) != len(positions):
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="Duplicate positions in reorder payload.",
            )

        existing_ids = {s.statusID for s in StatusRepository.get_all(db)}
        missing = [sid for sid in ids if sid not in existing_ids]
        if missing:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Statuses not found: {missing}.",
            )

        reordered = StatusRepository.reorder(
            db,
            items=[(i.statusID, i.position) for i in items],
        )

        return {
            "message": "Statuses were reordered successfully.",
            "statuses": reordered,
        }