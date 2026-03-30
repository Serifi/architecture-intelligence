import pytest
from fastapi import status

class TestProjectEndpoints:

    def test_list_projects_empty(self, client, sample_user):
        response = client.get(f"/projects/?user_id={sample_user.userID}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_projects_with_data(self, client, sample_project, sample_user):
        response = client.get(f"/projects/?user_id={sample_user.userID}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_project.name

    def test_get_project_success(self, client, sample_project, sample_user):
        response = client.get(f"/projects/{sample_project.projectID}?user_id={sample_user.userID}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["projectID"] == sample_project.projectID
        assert data["name"] == sample_project.name

    def test_get_project_not_found(self, client, sample_user):
        response = client.get(f"/projects/9999?user_id={sample_user.userID}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_project_success(self, client, sample_user):
        payload = {
            "name": "New API Project",
            "description": "Created via API",
            "priority": "high",
            "position": 0,
            "icon": "search",
            "color": "#FF5733",
            "tags": ["api", "test"],
        }
        response = client.post(f"/projects/?user_id={sample_user.userID}", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "message" in data
        assert data["project"]["name"] == "New API Project"

    def test_create_project_duplicate_name(self, client, sample_project, sample_user):
        payload = {
            "name": sample_project.name,
            "description": "Duplicate",
            "priority": "low",
            "position": 1,
            "icon": "search",
            "color": "#4A90E2",
        }
        response = client.post(f"/projects/?user_id={sample_user.userID}", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_update_project_success(self, client, sample_project, sample_user):
        payload = {"name": "Updated Name"}
        response = client.put(f"/projects/{sample_project.projectID}?user_id={sample_user.userID}", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["project"]["name"] == "Updated Name"

    def test_update_project_no_fields(self, client, sample_project, sample_user):
        payload = {}
        response = client.put(f"/projects/{sample_project.projectID}?user_id={sample_user.userID}", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_project_success(self, client, sample_project, sample_user):
        response = client.delete(f"/projects/{sample_project.projectID}?user_id={sample_user.userID}")
        assert response.status_code == status.HTTP_200_OK
        
        get_response = client.get(f"/projects/{sample_project.projectID}?user_id={sample_user.userID}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_not_found(self, client, sample_user):
        response = client.delete(f"/projects/9999?user_id={sample_user.userID}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reorder_projects(self, client, sample_project, sample_user, db_session):
        from backend.features.project.model import Project
        from backend.features.project.enum import PriorityLevel
        
        project2 = Project(
            userID=sample_user.userID,
            name="Project 2",
            description="Second",
            priority=PriorityLevel.LOW,
            position=1,
            icon="search",
            color="#123456",
        )
        db_session.add(project2)
        db_session.commit()
        
        payload = {
            "items": [
                {"projectID": project2.projectID, "position": 0},
                {"projectID": sample_project.projectID, "position": 1},
            ]
        }
        response = client.put(f"/projects/reorder?user_id={sample_user.userID}", json=payload)
        assert response.status_code == status.HTTP_200_OK

    def test_list_projects_filter_priority(self, client, sample_project, sample_user):
        response = client.get(f"/projects/?user_id={sample_user.userID}&priority=medium")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == "medium"
