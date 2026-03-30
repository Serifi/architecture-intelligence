from typing import Optional, List
from pydantic import BaseModel, Field, constr


class TemplateFieldBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=255)
    isRequired: bool = Field(default=False)


class TemplateFieldCreate(TemplateFieldBase):
    pass


class TemplateFieldUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    isRequired: Optional[bool] = None


class TemplateFieldRead(BaseModel):
    fieldID: int
    templateID: int
    name: str
    isRequired: bool

    model_config = {"from_attributes": True}


class DocumentationTemplateBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class DocumentationTemplateCreate(DocumentationTemplateBase):
    fields: Optional[List[TemplateFieldCreate]] = None


class DocumentationTemplateUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    description: Optional[str] = Field(None, max_length=2000)


class DocumentationTemplateRead(BaseModel):
    templateID: int
    name: str
    description: Optional[str]
    fields: List[TemplateFieldRead] = []

    model_config = {"from_attributes": True}