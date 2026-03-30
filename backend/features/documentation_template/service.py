from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.features.documentation_template.schema import (
    DocumentationTemplateCreate,
    DocumentationTemplateUpdate,
    TemplateFieldCreate,
    TemplateFieldUpdate,
)
from backend.features.documentation_template.repository import (
    DocumentationTemplateRepository,
)


class DocumentationTemplateService:
    @staticmethod
    def list_templates(db: Session):
        return DocumentationTemplateRepository.get_all(db)

    @staticmethod
    def get_template(db: Session, template_id: int):
        template = DocumentationTemplateRepository.get_by_id(db, template_id)
        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        return template

    @staticmethod
    def create_template(db: Session, payload: DocumentationTemplateCreate):
        template = DocumentationTemplateRepository.create(
            db,
            name=payload.name,
            description=payload.description,
        )

        if payload.fields:
            for field_payload in payload.fields:
                DocumentationTemplateService.add_field(
                    db=db,
                    template_id=template.templateID,
                    payload=field_payload,
                )
            db.refresh(template)

        return template

    @staticmethod
    def update_template(db: Session, template_id: int, payload: DocumentationTemplateUpdate):
        template = DocumentationTemplateService.get_template(db, template_id)
        return DocumentationTemplateRepository.update(
            db,
            template=template,
            name=payload.name,
            description=payload.description,
        )

    @staticmethod
    def delete_template(db: Session, template_id: int):
        template = DocumentationTemplateService.get_template(db, template_id)
        DocumentationTemplateRepository.delete(db, template)
        return {"deleted": True}

    @staticmethod
    def list_fields(db: Session, template_id: int):
        DocumentationTemplateService.get_template(db, template_id)
        return DocumentationTemplateRepository.get_fields_for_template(db, template_id)

    @staticmethod
    def add_field(db: Session, template_id: int, payload: TemplateFieldCreate):
        DocumentationTemplateService.get_template(db, template_id)
        return DocumentationTemplateRepository.add_field(
            db,
            template_id=template_id,
            name=payload.name,
            is_required=payload.isRequired,
        )

    @staticmethod
    def update_field(db: Session, field_id: int, payload: TemplateFieldUpdate):
        field = DocumentationTemplateRepository.get_field_by_id(db, field_id)
        if field is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template field not found",
            )

        return DocumentationTemplateRepository.update_field(
            db,
            field=field,
            name=payload.name,
            is_required=payload.isRequired,
        )

    @staticmethod
    def delete_field(db: Session, field_id: int):
        field = DocumentationTemplateRepository.get_field_by_id(db, field_id)
        if field is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template field not found",
            )

        DocumentationTemplateRepository.delete_field(db, field)
        return {"deleted": True}