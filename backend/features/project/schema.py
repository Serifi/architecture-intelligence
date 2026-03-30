from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, constr, field_validator
from backend.features.project.enum import PriorityLevel
import re


class ProjectBase(BaseModel):
    name: constr(strip_whitespace=True, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    position: int = Field(0, ge=0)
    icon: constr(strip_whitespace=True, min_length=1, max_length=255)
    color: constr(strip_whitespace=True, min_length=1, max_length=50)
    tags: Optional[List[str]] = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v is None:
            raise ValueError("Color is required.")
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", v):
            raise ValueError("Color must be a valid HEX code, e.g. '#4A90E2'.")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("Maximum of 10 tags allowed.")
        for tag in v:
            if not tag.strip():
                raise ValueError("Tags cannot be empty.")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, max_length=255)] = None
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[PriorityLevel] = None
    position: Optional[int] = Field(None, ge=0)
    icon: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    color: Optional[constr(strip_whitespace=True, min_length=1, max_length=50)] = None
    tags: Optional[List[str]] = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if v is None:
            return v
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", v):
            raise ValueError("Color must be a valid HEX code, e.g. '#4A90E2'.")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("Maximum of 10 tags allowed.")
        for tag in v:
            if not tag.strip():
                raise ValueError("Tags cannot be empty.")
        return v


class ProjectRead(BaseModel):
    projectID: int
    name: str
    description: Optional[str]
    priority: PriorityLevel
    position: int
    icon: str
    color: str
    creationDate: datetime
    lastUpdated: datetime
    tags: Optional[List[str]]

    model_config = {"from_attributes": True}


class ProjectReorderItem(BaseModel):
    projectID: int = Field(..., ge=1)
    position: int = Field(..., ge=0)


class ProjectReorderPayload(BaseModel):
    items: List[ProjectReorderItem]