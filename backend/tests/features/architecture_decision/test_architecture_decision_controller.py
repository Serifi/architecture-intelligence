import pytest
from fastapi import status


class TestDecisionEndpoints:

    def test_list_decisions_empty(self, client, sample_project):
        response = client.get(f"/decisions/?project_id={sample_project.projectID}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_decisions_with_data(self, client, sample_decision):
        response = client.get(f"/decisions/?project_id={sample_decision.projectID}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_decision.title

    def test_list_all_summaries(self, client, sample_decision):
        response = client.get("/decisions/summaries")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_decision.title

    def test_get_decision_success(self, client, sample_decision):
        response = client.get(f"/decisions/{sample_decision.decisionID}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["decisionID"] == sample_decision.decisionID
        assert data["title"] == sample_decision.title

    def test_get_decision_not_found(self, client):
        response = client.get("/decisions/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_decision_documentation(self, client, sample_decision):
        response = client.get(f"/decisions/{sample_decision.decisionID}/documentation")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["decisionID"] == sample_decision.decisionID
        assert "fields" in data
        assert "templateName" in data

    def test_create_decision_success(
        self, client, sample_project, sample_template_with_fields, sample_status, sample_user
    ):
        required_fields = [f for f in sample_template_with_fields.fields if f.isRequired]
        field_values = [
            {"fieldID": f.fieldID, "value": f"Value for {f.name}"}
            for f in required_fields
        ]
        
        payload = {
            "projectID": sample_project.projectID,
            "templateID": sample_template_with_fields.templateID,
            "statusID": sample_status.statusID,
            "title": "New Decision",
            "userID": sample_user.userID,
            "fieldValues": field_values,
        }
        response = client.post("/decisions/", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "message" in data
        assert data["decision"]["title"] == "New Decision"

    def test_create_decision_missing_required_fields(
        self, client, sample_project, sample_template_with_fields, sample_status, sample_user
    ):
        payload = {
            "projectID": sample_project.projectID,
            "templateID": sample_template_with_fields.templateID,
            "statusID": sample_status.statusID,
            "title": "Decision Without Fields",
            "userID": sample_user.userID,
            "fieldValues": [],
        }
        response = client.post("/decisions/", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_decision_success(self, client, sample_decision, sample_user):
        payload = {
            "userID": sample_user.userID,
            "title": "Updated Decision Title",
        }
        response = client.put(f"/decisions/{sample_decision.decisionID}", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["decision"]["title"] == "Updated Decision Title"

    def test_update_decision_not_found(self, client, sample_user):
        payload = {"userID": sample_user.userID, "title": "New Title"}
        response = client.put("/decisions/9999", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_decision_success(self, client, sample_decision):
        response = client.delete(f"/decisions/{sample_decision.decisionID}")
        assert response.status_code == status.HTTP_200_OK
        
        get_response = client.get(f"/decisions/{sample_decision.decisionID}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_decision_not_found(self, client):
        response = client.delete("/decisions/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
