from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.documentation_template.schema import (
    DocumentationTemplateCreate,
    DocumentationTemplateUpdate,
    DocumentationTemplateRead,
    TemplateFieldCreate,
    TemplateFieldUpdate,
    TemplateFieldRead,
)
from backend.features.documentation_template.service import DocumentationTemplateService

router = APIRouter(prefix="/templates", tags=["templates"])



@router.get("/", response_model=List[DocumentationTemplateRead])
def list_templates(db: Session = Depends(get_db)):
    return DocumentationTemplateService.list_templates(db)


@router.get("/{template_id}", response_model=DocumentationTemplateRead)
def get_template(
    template_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return DocumentationTemplateService.get_template(db, template_id)


@router.post(
    "/",
    response_model=DocumentationTemplateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_template(
    payload: DocumentationTemplateCreate = Body(...),
    db: Session = Depends(get_db),
):
    return DocumentationTemplateService.create_template(db, payload)


@router.put("/{template_id}", response_model=DocumentationTemplateRead)
def update_template(
    template_id: int = Path(..., ge=1),
    payload: DocumentationTemplateUpdate = Body(...),
    db: Session = Depends(get_db),
):
    if payload.name is None and payload.description is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update payload must contain at least one field.",
        )

    return DocumentationTemplateService.update_template(db, template_id, payload)


@router.delete("/{template_id}", status_code=status.HTTP_200_OK)
def delete_template(
    template_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return DocumentationTemplateService.delete_template(db, template_id)



@router.get(
    "/{template_id}/fields",
    response_model=List[TemplateFieldRead],
)
def list_fields_for_template(
    template_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return DocumentationTemplateService.list_fields(db, template_id)


@router.post(
    "/{template_id}/fields",
    response_model=TemplateFieldRead,
    status_code=status.HTTP_201_CREATED,
)
def add_field_to_template(
    template_id: int = Path(..., ge=1),
    payload: TemplateFieldCreate = Body(...),
    db: Session = Depends(get_db),
):
    return DocumentationTemplateService.add_field(db, template_id, payload)


@router.put(
    "/fields/{field_id}",
    response_model=TemplateFieldRead,
)
def update_field(
    field_id: int = Path(..., ge=1),
    payload: TemplateFieldUpdate = Body(...),
    db: Session = Depends(get_db),
):
    if payload.name is None and payload.isRequired is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update payload must contain at least one field.",
        )

    return DocumentationTemplateService.update_field(db, field_id, payload)


@router.delete(
    "/fields/{field_id}",
    status_code=status.HTTP_200_OK,
)
def delete_field(
    field_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return DocumentationTemplateService.delete_field(db, field_id)