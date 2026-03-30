import shutil

from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.features.project.schema import ProjectCreate, ProjectUpdate, ProjectReorderPayload
from backend.features.project.repository import ProjectRepository
from backend.features.project.enum import PriorityLevel

ATTACHMENTS_DIR = str(Path(__file__).resolve().parents[2] / "resources" / "attachments")

class ProjectService:
    @staticmethod
    def list_projects(db: Session, user_id: int):
        return ProjectRepository.get_all_for_user(db, user_id)

    @staticmethod
    def get_project(db: Session, project_id: int, user_id: int):
        project = ProjectRepository.get_by_id(db, project_id)
        if project is None or project.userID != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )
        return project

    @staticmethod
    def create_project(db: Session, payload: ProjectCreate, user_id: int):
        existing = ProjectRepository.get_by_name_for_user(db, payload.name, user_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project '{payload.name}' cannot be created: name already exists.",
            )

        if payload.priority not in PriorityLevel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority must be one of: low, medium, high, critical.",
            )

        project = ProjectRepository.create(
            db,
            user_id=user_id,
            name=payload.name,
            description=payload.description,
            priority=payload.priority,
            position=payload.position,
            icon=payload.icon,
            color=payload.color,
            tags=payload.tags,
        )
        return {
            "message": f"Project '{project.name}' was created successfully.",
            "project": project,
        }

    @staticmethod
    def update_project(db: Session, project_id: int, payload: ProjectUpdate, user_id: int):
        project = ProjectService.get_project(db, project_id, user_id)

        if payload.name is not None and payload.name.lower() != project.name.lower():
            existing = ProjectRepository.get_by_name_for_user(db, payload.name, user_id)
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Project '{payload.name}' cannot be updated: name already exists.",
                )

        if payload.priority is not None and payload.priority not in PriorityLevel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority must be one of: low, medium, high, critical.",
            )

        updated = ProjectRepository.update(
            db,
            project=project,
            name=payload.name,
            description=payload.description,
            priority=payload.priority,
            position=payload.position,
            icon=payload.icon,
            color=payload.color,
            tags=payload.tags,
        )
        return {
            "message": f"Project '{updated.name}' was updated successfully.",
            "project": updated,
        }

    @staticmethod
    def reorder_projects(db: Session, payload: ProjectReorderPayload, user_id: int):
        if not payload.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reorder payload must not be empty.",
            )

        ProjectRepository.reorder(db, user_id, payload.items)
        return {"message": "Projects reordered successfully."}

    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int):
        project = ProjectService.get_project(db, project_id, user_id)

        project_dir = Path(ATTACHMENTS_DIR) / str(project.projectID)
        try:
            if project_dir.exists():
                if not project_dir.is_dir():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Expected attachment path to be a directory: {project_dir}",
                    )
                shutil.rmtree(project_dir)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not delete attachments folder: {project_dir} ({e})",
            )

        ProjectRepository.delete(db, project)
        return {"message": f"Project '{project.name}' was deleted successfully."}