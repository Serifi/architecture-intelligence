from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.features.documentation_template.model import DocumentationTemplate
from backend.features.documentation_template.fields.model import DocumentationTemplateField


class DocumentationTemplateRepository:
    @staticmethod
    def get_all(db: Session) -> List[DocumentationTemplate]:
        return db.execute(select(DocumentationTemplate)).scalars().all()

    @staticmethod
    def get_by_id(db: Session, template_id: int) -> Optional[DocumentationTemplate]:
        return db.get(DocumentationTemplate, template_id)

    @staticmethod
    def create(db: Session, name: str, description: str | None) -> DocumentationTemplate:
        template = DocumentationTemplate(
            name=name,
            description=description,
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def update(db: Session, template: DocumentationTemplate, name: str | None, description: str | None) -> DocumentationTemplate:
        if name is not None:
            template.name = name
        if description is not None:
            template.description = description

        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def delete(db: Session, template: DocumentationTemplate) -> None:
        db.delete(template)
        db.commit()

    @staticmethod
    def get_field_by_id(db: Session, field_id: int) -> Optional[DocumentationTemplateField]:
        return db.get(DocumentationTemplateField, field_id)

    @staticmethod
    def get_fields_for_template(db: Session, template_id: int) -> List[DocumentationTemplateField]:
        stmt = select(DocumentationTemplateField).where(DocumentationTemplateField.templateID == template_id)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def add_field(db: Session, template_id: int, name: str, is_required: bool) -> DocumentationTemplateField:
        field = DocumentationTemplateField(
            templateID=template_id,
            name=name,
            isRequired=is_required,
        )
        db.add(field)
        db.commit()
        db.refresh(field)
        return field

    @staticmethod
    def update_field(db: Session, field: DocumentationTemplateField, name: str | None, is_required: bool | None) -> DocumentationTemplateField:
        if name is not None:
            field.name = name
        if is_required is not None:
            field.isRequired = is_required

        db.commit()
        db.refresh(field)
        return field

    @staticmethod
    def delete_field(db: Session, field: DocumentationTemplateField) -> None:
        db.delete(field)
        db.commit()