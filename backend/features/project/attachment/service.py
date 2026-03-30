import os
from pathlib import Path

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from backend.features.project.service import ProjectService
from backend.features.project.attachment.repository import ProjectAttachmentRepository

ATTACHMENTS_DIR = str(Path(__file__).resolve().parents[3] / "resources" / "attachments")
MAX_ATTACHMENT_SIZE_MB = 50
MAX_ATTACHMENT_SIZE_BYTES = MAX_ATTACHMENT_SIZE_MB * 1024 * 1024
MAX_ATTACHMENT_SIZE_MB = MAX_ATTACHMENT_SIZE_BYTES // (1024 * 1024)


class ProjectAttachmentService:
    @staticmethod
    def list_attachments(db: Session, project_id: int, user_id: int):
        ProjectService.get_project(db, project_id, user_id)
        return ProjectAttachmentRepository.list_for_project(db, project_id)

    @staticmethod
    def upload_attachment(db: Session, project_id: int, user_id: int, file: UploadFile):
        ProjectService.get_project(db, project_id, user_id)

        filename = file.filename or ""

        if not filename.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File could not be uploaded: filename is empty.",
            )

        if ProjectAttachmentRepository.exists_with_original_filename(db, project_id, filename):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'"{filename}" could not be uploaded: file already added.',
            )

        content = file.file.read()
        size = len(content)

        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'"{filename}" could not be uploaded: file is empty.',
            )

        if size > MAX_ATTACHMENT_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f'"{filename}" could not be uploaded: '
                    f'file exceeds {MAX_ATTACHMENT_SIZE_MB}MB limit.'
                ),
            )

        os.makedirs(f"{ATTACHMENTS_DIR}/{project_id}", exist_ok=True)

        attachment = ProjectAttachmentRepository.create(
            db,
            project_id=project_id,
            user_id=user_id,
            filename=filename,
            mimetype=file.content_type or "application/octet-stream",
            size=size,
        )

        path = f"{ATTACHMENTS_DIR}/{project_id}/{attachment.storedFilename}"

        with open(path, "wb") as f:
          f.write(content)

        return attachment


    @staticmethod
    def delete_attachment(db: Session, project_id: int, attachment_id: int, user_id: int):
        ProjectService.get_project(db, project_id, user_id)

        attachment = ProjectAttachmentRepository.get_by_id(db, attachment_id)
        if attachment is None or attachment.projectID != project_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found.",
            )

        filename = attachment.originalFilename
        path = f"{ATTACHMENTS_DIR}/{project_id}/{attachment.storedFilename}"

        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'"{filename}" could not be deleted: internal server error.',
                )

        ProjectAttachmentRepository.delete(db, attachment)

        return {"message": f'"{filename}" was deleted successfully.'}