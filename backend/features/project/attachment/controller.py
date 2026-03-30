from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Query, Path, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.project.attachment.schema import ProjectAttachmentRead
from backend.features.project.attachment.service import ProjectAttachmentService


router = APIRouter(prefix="/projects/{project_id}/attachments", tags=["project-attachments"])


@router.get("/", response_model=List[ProjectAttachmentRead])
def list_files(
    project_id: int = Path(..., ge=1),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ProjectAttachmentService.list_attachments(db, project_id, user_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_file(
    project_id: int = Path(..., ge=1),
    user_id: int = Query(..., ge=1),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    attachment = ProjectAttachmentService.upload_attachment(db, project_id, user_id, file)
    return {
        "message": f'"{attachment.originalFilename}" uploaded successfully.',
        "attachment": attachment,
    }


@router.delete("/{attachment_id}", status_code=status.HTTP_200_OK)
def delete_file(
    project_id: int = Path(..., ge=1),
    attachment_id: int = Path(..., ge=1),
    user_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ProjectAttachmentService.delete_attachment(db, project_id, attachment_id, user_id)