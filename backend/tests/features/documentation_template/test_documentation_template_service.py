import pytest
from fastapi import HTTPException

from backend.features.documentation_template.service import DocumentationTemplateService
from backend.features.documentation_template.schema import (
    DocumentationTemplateCreate,
    DocumentationTemplateUpdate,
    TemplateFieldCreate,
    TemplateFieldUpdate,
)


class TestDocumentationTemplateServiceListTemplates:

    def test_list_templates_empty(self, db_session):
        result = DocumentationTemplateService.list_templates(db_session)
        assert result == []

    def test_list_templates_with_data(self, db_session, sample_template):
        result = DocumentationTemplateService.list_templates(db_session)
        assert len(result) == 1
        assert result[0].name == sample_template.name


class TestDocumentationTemplateServiceGetTemplate:

    def test_get_template_success(self, db_session, sample_template):
        result = DocumentationTemplateService.get_template(db_session, sample_template.templateID)
        assert result.templateID == sample_template.templateID
        assert result.name == sample_template.name

    def test_get_template_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.get_template(db_session, 9999)
        assert exc_info.value.status_code == 404
        assert "Template not found" in exc_info.value.detail


class TestDocumentationTemplateServiceCreateTemplate:

    def test_create_template_success(self, db_session):
        payload = DocumentationTemplateCreate(
            name="New Template",
            description="A new template",
        )
        result = DocumentationTemplateService.create_template(db_session, payload)
        
        assert result.name == "New Template"
        assert result.description == "A new template"

    def test_create_template_with_fields(self, db_session):
        payload = DocumentationTemplateCreate(
            name="Template with Fields",
            description="Has fields",
            fields=[
                TemplateFieldCreate(name="Title", isRequired=True),
                TemplateFieldCreate(name="Notes", isRequired=False),
            ],
        )
        result = DocumentationTemplateService.create_template(db_session, payload)
        
        assert result.name == "Template with Fields"
        assert len(result.fields) == 2


class TestDocumentationTemplateServiceUpdateTemplate:

    def test_update_template_success(self, db_session, sample_template):
        payload = DocumentationTemplateUpdate(
            name="Updated Template",
            description="Updated description",
        )
        result = DocumentationTemplateService.update_template(
            db_session, sample_template.templateID, payload
        )
        
        assert result.name == "Updated Template"
        assert result.description == "Updated description"

    def test_update_template_not_found(self, db_session):
        payload = DocumentationTemplateUpdate(name="New Name")
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.update_template(db_session, 9999, payload)
        assert exc_info.value.status_code == 404


class TestDocumentationTemplateServiceDeleteTemplate:

    def test_delete_template_success(self, db_session, sample_template):
        template_id = sample_template.templateID
        result = DocumentationTemplateService.delete_template(db_session, template_id)
        
        assert result["deleted"] is True
        
        with pytest.raises(HTTPException):
            DocumentationTemplateService.get_template(db_session, template_id)

    def test_delete_template_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.delete_template(db_session, 9999)
        assert exc_info.value.status_code == 404


class TestDocumentationTemplateServiceFields:

    def test_list_fields(self, db_session, sample_template_with_fields):
        result = DocumentationTemplateService.list_fields(
            db_session, sample_template_with_fields.templateID
        )
        assert len(result) == 3

    def test_list_fields_template_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.list_fields(db_session, 9999)
        assert exc_info.value.status_code == 404

    def test_add_field_success(self, db_session, sample_template):
        payload = TemplateFieldCreate(name="New Field", isRequired=True)
        result = DocumentationTemplateService.add_field(
            db_session, sample_template.templateID, payload
        )
        
        assert result.name == "New Field"
        assert result.isRequired is True

    def test_add_field_template_not_found(self, db_session):
        payload = TemplateFieldCreate(name="Field", isRequired=False)
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.add_field(db_session, 9999, payload)
        assert exc_info.value.status_code == 404

    def test_update_field_success(self, db_session, sample_template_with_fields):
        field = sample_template_with_fields.fields[0]
        payload = TemplateFieldUpdate(name="Updated Field Name", isRequired=False)
        result = DocumentationTemplateService.update_field(db_session, field.fieldID, payload)
        
        assert result.name == "Updated Field Name"
        assert result.isRequired is False

    def test_update_field_not_found(self, db_session):
        payload = TemplateFieldUpdate(name="New Name")
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.update_field(db_session, 9999, payload)
        assert exc_info.value.status_code == 404

    def test_delete_field_success(self, db_session, sample_template_with_fields):
        field = sample_template_with_fields.fields[0]
        result = DocumentationTemplateService.delete_field(db_session, field.fieldID)
        
        assert result["deleted"] is True

    def test_delete_field_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            DocumentationTemplateService.delete_field(db_session, 9999)
        assert exc_info.value.status_code == 404
