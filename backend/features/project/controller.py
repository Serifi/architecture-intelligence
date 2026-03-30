from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.project.schema import ProjectCreate, ProjectUpdate, ProjectRead, ProjectReorderPayload
from backend.features.project.enum import PriorityLevel
from backend.features.project.service import ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.put("/reorder", status_code=status.HTTP_200_OK)
def reorder_projects(
    payload: ProjectReorderPayload = Body(...),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ProjectService.reorder_projects(db, payload, user_id)


@router.get("/", response_model=List[ProjectRead])
def list_projects(
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    priority: Optional[PriorityLevel] = Query(default=None),
):
    projects = ProjectService.list_projects(db, user_id)
    if priority is not None:
        projects = [p for p in projects if p.priority == priority]
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int = Path(..., ge=1),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ProjectService.get_project(db, project_id, user_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate = Body(...),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ProjectService.create_project(db, payload, user_id)


@router.put("/{project_id}")
def update_project(
    project_id: int = Path(..., ge=1),
    payload: ProjectUpdate = Body(...),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    if (
        payload.name is None
        and payload.description is None
        and payload.priority is None
        and payload.position is None
        and payload.icon is None
        and payload.color is None
        and payload.tags is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update payload must contain at least one field.",
        )

    return ProjectService.update_project(db, project_id, payload, user_id)


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int = Path(..., ge=1),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ProjectService.delete_project(db, project_id, user_id)