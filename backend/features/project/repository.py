from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.features.project.model import Project
from backend.features.project.enum import PriorityLevel
from backend.features.project.schema import ProjectReorderItem


class ProjectRepository:
    @staticmethod
    def get_all_for_user(db: Session, user_id: int):
        stmt = (
            select(Project)
            .where(Project.userID == user_id)
            .order_by(Project.position, Project.projectID)
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        return db.get(Project, project_id)

    @staticmethod
    def get_by_name_for_user(db: Session, name: str, user_id: int) -> Optional[Project]:
        return (
            db.query(Project)
            .filter(
                Project.userID == user_id,
                func.lower(Project.name) == name.lower(),
            )
            .first()
        )

    @staticmethod
    def create(db: Session, user_id: int, name: str, description: str | None, priority: PriorityLevel, position: int, icon: str, color: str, tags: list[str] | None):
        project = Project(
            userID=user_id,
            name=name,
            description=description,
            priority=priority,
            position=position,
            icon=icon,
            color=color,
            tags=tags,
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update(db: Session, project: Project, name: str | None, description: str | None, priority: PriorityLevel | None, position: int | None, icon: str | None, color: str | None, tags: list[str] | None):
        content_changed = False

        if name is not None:
            project.name = name
            content_changed = True

        if description is not None:
            project.description = description
            content_changed = True

        if priority is not None:
            project.priority = priority
            content_changed = True

        if icon is not None:
            project.icon = icon
            content_changed = True

        if color is not None:
            project.color = color
            content_changed = True

        if tags is not None:
            project.tags = tags
            content_changed = True

        if position is not None:
            project.position = position

        if content_changed:
            project.lastUpdated = datetime.now(timezone.utc)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def reorder(db: Session, user_id: int, items: List[ProjectReorderItem]) -> None:
        ids = [i.projectID for i in items]
        projects = (
            db.query(Project)
            .filter(Project.projectID.in_(ids), Project.userID == user_id)
            .all()
        )
        by_id = {p.projectID: p for p in projects}

        for it in items:
            p = by_id.get(it.projectID)
            if p is not None:
                p.position = (p.position or 0) + 1000
        db.flush()

        for it in items:
            p = by_id.get(it.projectID)
            if p is not None:
                p.position = it.position

        db.commit()

    @staticmethod
    def delete(db: Session, project: Project):
        db.delete(project)
        db.commit()