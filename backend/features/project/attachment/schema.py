from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectAttachmentBase(BaseModel):
    originalFilename: str
    mimeType: str
    sizeBytes: int


class ProjectAttachmentRead(ProjectAttachmentBase):
    attachmentID: int
    storedFilename: str
    createdAt: datetime

    model_config = {"from_attributes": True}