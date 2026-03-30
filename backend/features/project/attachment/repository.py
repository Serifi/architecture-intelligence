import os
import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.features.project.attachment.model import ProjectAttachment


class ProjectAttachmentRepository:
    @staticmethod
    def list_for_project(db: Session, project_id: int) -> List[ProjectAttachment]:
        stmt = (
            select(ProjectAttachment)
            .where(ProjectAttachment.projectID == project_id)
            .order_by(ProjectAttachment.createdAt.desc())
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, attachment_id: int) -> Optional[ProjectAttachment]:
        return db.get(ProjectAttachment, attachment_id)

    @staticmethod
    def exists_with_original_filename(db: Session, project_id: int, filename: str) -> bool:
        stmt = (
            select(func.count())
            .select_from(ProjectAttachment)
            .where(
                ProjectAttachment.projectID == project_id,
                ProjectAttachment.originalFilename == filename,
            )
        )
        count = db.execute(stmt).scalar_one()
        return count > 0

    @staticmethod
    def create(db: Session, project_id: int, user_id: int, filename: str, mimetype: str, size: int):
        ext = filename.split(".")[-1] if "." in filename else ""
        stored = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())

        attachment = ProjectAttachment(
            projectID=project_id,
            uploadedByUserID=user_id,
            originalFilename=filename,
            storedFilename=stored,
            mimeType=mimetype,
            sizeBytes=size,
        )

        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return attachment

    @staticmethod
    def delete(db: Session, attachment: ProjectAttachment):
        db.delete(attachment)
        db.commit()