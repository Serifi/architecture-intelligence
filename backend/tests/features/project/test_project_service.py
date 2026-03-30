import pytest
from fastapi import HTTPException

from backend.features.project.service import ProjectService
from backend.features.project.schema import ProjectCreate, ProjectUpdate, ProjectReorderPayload, ProjectReorderItem
from backend.features.project.enum import PriorityLevel
from backend.features.project.model import Project


class TestProjectServiceListProjects:

    def test_list_projects_empty(self, db_session, sample_user):
        result = ProjectService.list_projects(db_session, sample_user.userID)
        assert result == []

    def test_list_projects_with_data(self, db_session, sample_project, sample_user):
        result = ProjectService.list_projects(db_session, sample_user.userID)
        assert len(result) == 1
        assert result[0].name == sample_project.name


class TestProjectServiceGetProject:

    def test_get_project_success(self, db_session, sample_project, sample_user):
        result = ProjectService.get_project(db_session, sample_project.projectID, sample_user.userID)
        assert result.projectID == sample_project.projectID
        assert result.name == sample_project.name

    def test_get_project_not_found(self, db_session, sample_user):
        with pytest.raises(HTTPException) as exc_info:
            ProjectService.get_project(db_session, 9999, sample_user.userID)
        assert exc_info.value.status_code == 404
        assert "Project not found" in exc_info.value.detail


class TestProjectServiceCreateProject:

    def test_create_project_success(self, db_session, sample_user):
        payload = ProjectCreate(
            name="New Project",
            description="A new project",
            priority=PriorityLevel.HIGH,
            position=0,
            icon="search",
            color="#FF5733",
            tags=["new", "important"],
        )
        result = ProjectService.create_project(db_session, payload, sample_user.userID)
        
        assert "message" in result
        assert "project" in result
        assert result["project"].name == "New Project"
        assert result["project"].priority == PriorityLevel.HIGH

    def test_create_project_duplicate_name(self, db_session, sample_project, sample_user):
        payload = ProjectCreate(
            name=sample_project.name,
            description="Duplicate project",
            priority=PriorityLevel.LOW,
            position=1,
            icon="search",
            color="#4A90E2",
        )
        with pytest.raises(HTTPException) as exc_info:
            ProjectService.create_project(db_session, payload, sample_user.userID)
        assert exc_info.value.status_code == 409
        assert "name already exists" in exc_info.value.detail


class TestProjectServiceUpdateProject:

    def test_update_project_success(self, db_session, sample_project, sample_user):
        payload = ProjectUpdate(
            name="Updated Project Name",
            description="Updated description",
        )
        result = ProjectService.update_project(db_session, sample_project.projectID, payload, sample_user.userID)
        
        assert "message" in result
        assert "project" in result
        assert result["project"].name == "Updated Project Name"
        assert result["project"].description == "Updated description"

    def test_update_project_not_found(self, db_session, sample_user):
        payload = ProjectUpdate(name="New Name")
        with pytest.raises(HTTPException) as exc_info:
            ProjectService.update_project(db_session, 9999, payload, sample_user.userID)
        assert exc_info.value.status_code == 404

    def test_update_project_duplicate_name(self, db_session, sample_project, sample_user):
        project2 = Project(
            userID=sample_user.userID,
            name="Another Project",
            description="Second project",
            priority=PriorityLevel.LOW,
            position=1,
            icon="search",
            color="#123456",
        )
        db_session.add(project2)
        db_session.commit()

        payload = ProjectUpdate(name="Another Project")
        with pytest.raises(HTTPException) as exc_info:
            ProjectService.update_project(db_session, sample_project.projectID, payload, sample_user.userID)
        assert exc_info.value.status_code == 409
        assert "name already exists" in exc_info.value.detail

    def test_update_project_priority(self, db_session, sample_project, sample_user):
        payload = ProjectUpdate(priority=PriorityLevel.CRITICAL)
        result = ProjectService.update_project(db_session, sample_project.projectID, payload, sample_user.userID)
        assert result["project"].priority == PriorityLevel.CRITICAL


class TestProjectServiceDeleteProject:

    def test_delete_project_success(self, db_session, sample_project, sample_user):
        project_id = sample_project.projectID
        result = ProjectService.delete_project(db_session, project_id, sample_user.userID)
        
        assert "message" in result
        assert "deleted successfully" in result["message"]
        
        with pytest.raises(HTTPException):
            ProjectService.get_project(db_session, project_id, sample_user.userID)

    def test_delete_project_not_found(self, db_session, sample_user):
        with pytest.raises(HTTPException) as exc_info:
            ProjectService.delete_project(db_session, 9999, sample_user.userID)
        assert exc_info.value.status_code == 404


class TestProjectServiceReorderProjects:

    def test_reorder_projects_success(self, db_session, sample_project, sample_user):
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

        payload = ProjectReorderPayload(
            items=[
                ProjectReorderItem(projectID=project2.projectID, position=0),
                ProjectReorderItem(projectID=sample_project.projectID, position=1),
            ]
        )
        result = ProjectService.reorder_projects(db_session, payload, sample_user.userID)
        assert "message" in result
        assert "reordered successfully" in result["message"]

    def test_reorder_projects_empty_payload(self, db_session, sample_user):
        payload = ProjectReorderPayload(items=[])
        with pytest.raises(HTTPException) as exc_info:
            ProjectService.reorder_projects(db_session, payload, sample_user.userID)
        assert exc_info.value.status_code == 400
        assert "must not be empty" in exc_info.value.detail
