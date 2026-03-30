import pytest
from fastapi import status


class TestDocumentationTemplateEndpoints:

    def test_list_templates_empty(self, client):
        response = client.get("/templates/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_templates_with_data(self, client, sample_template):
        response = client.get("/templates/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_template.name

    def test_get_template_success(self, client, sample_template):
        response = client.get(f"/templates/{sample_template.templateID}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["templateID"] == sample_template.templateID
        assert data["name"] == sample_template.name

    def test_get_template_not_found(self, client):
        response = client.get("/templates/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_template_success(self, client):
        payload = {
            "name": "New Template",
            "description": "A new template",
        }
        response = client.post("/templates/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Template"

    def test_create_template_with_fields(self, client):
        payload = {
            "name": "Template with Fields",
            "description": "Has fields",
            "fields": [
                {"name": "Title", "isRequired": True},
                {"name": "Notes", "isRequired": False},
            ],
        }
        response = client.post("/templates/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Template with Fields"
        assert len(data["fields"]) == 2

    def test_update_template_success(self, client, sample_template):
        payload = {"name": "Updated Template"}
        response = client.put(f"/templates/{sample_template.templateID}", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Template"

    def test_update_template_no_fields(self, client, sample_template):
        payload = {}
        response = client.put(f"/templates/{sample_template.templateID}", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_template_success(self, client, sample_template):
        response = client.delete(f"/templates/{sample_template.templateID}")
        assert response.status_code == status.HTTP_200_OK
        
        get_response = client.get(f"/templates/{sample_template.templateID}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestDocumentationTemplateFieldEndpoints:

    def test_list_fields(self, client, sample_template_with_fields):
        response = client.get(f"/templates/{sample_template_with_fields.templateID}/fields")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_fields_template_not_found(self, client):
        response = client.get("/templates/9999/fields")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_field_success(self, client, sample_template):
        payload = {"name": "New Field", "isRequired": True}
        response = client.post(
            f"/templates/{sample_template.templateID}/fields", 
            json=payload
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Field"
        assert data["isRequired"] is True

    def test_update_field_success(self, client, sample_template_with_fields):
        field = sample_template_with_fields.fields[0]
        payload = {"name": "Updated Field Name", "isRequired": False}
        response = client.put(f"/templates/fields/{field.fieldID}", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Field Name"

    def test_delete_field_success(self, client, sample_template_with_fields):
        field = sample_template_with_fields.fields[0]
        response = client.delete(f"/templates/fields/{field.fieldID}")
        assert response.status_code == status.HTTP_200_OK
