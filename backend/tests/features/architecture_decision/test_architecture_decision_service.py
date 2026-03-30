import pytest
from fastapi import HTTPException

from backend.features.architecture_decision.service import ArchitectureDecisionService
from backend.features.architecture_decision.schema import (
    ArchitectureDecisionCreate,
    ArchitectureDecisionUpdate,
    DecisionFieldValueCreate,
)
from backend.features.architecture_decision.model import ArchitectureDecision


class TestArchitectureDecisionServiceListByProject:

    def test_list_by_project_empty(self, db_session, sample_project):
        result = ArchitectureDecisionService.list_by_project(db_session, sample_project.projectID)
        assert result == []

    def test_list_by_project_with_data(self, db_session, sample_decision):
        result = ArchitectureDecisionService.list_by_project(
            db_session, sample_decision.projectID
        )
        assert len(result) == 1
        assert result[0].title == sample_decision.title


class TestArchitectureDecisionServiceListAll:

    def test_list_all_empty(self, db_session):
        result = ArchitectureDecisionService.list_all(db_session)
        assert result == []

    def test_list_all_with_data(self, db_session, sample_decision):
        result = ArchitectureDecisionService.list_all(db_session)
        assert len(result) == 1


class TestArchitectureDecisionServiceGet:

    def test_get_success(self, db_session, sample_decision):
        result = ArchitectureDecisionService.get(db_session, sample_decision.decisionID)
        assert result.decisionID == sample_decision.decisionID
        assert result.title == sample_decision.title

    def test_get_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.get(db_session, 9999)
        assert exc_info.value.status_code == 404
        assert "Architecture decision not found" in exc_info.value.detail


class TestArchitectureDecisionServiceCreate:

    def test_create_success(self, db_session, sample_project, sample_template_with_fields, sample_status, sample_user):
        required_fields = [f for f in sample_template_with_fields.fields if f.isRequired]
        field_values = [
            DecisionFieldValueCreate(fieldID=f.fieldID, value=f"Value for {f.name}")
            for f in required_fields
        ]
        
        payload = ArchitectureDecisionCreate(
            projectID=sample_project.projectID,
            templateID=sample_template_with_fields.templateID,
            statusID=sample_status.statusID,
            title="New Decision",
            userID=sample_user.userID,
            fieldValues=field_values,
        )
        result = ArchitectureDecisionService.create(db_session, payload)
        
        assert "message" in result
        assert "decision" in result
        assert result["decision"].title == "New Decision"

    def test_create_duplicate_title(self, db_session, sample_decision, sample_project, sample_template_with_fields, sample_status, sample_user):
        required_fields = [f for f in sample_template_with_fields.fields if f.isRequired]
        field_values = [
            DecisionFieldValueCreate(fieldID=f.fieldID, value=f"Value for {f.name}")
            for f in required_fields
        ]
        
        payload = ArchitectureDecisionCreate(
            projectID=sample_project.projectID,
            templateID=sample_template_with_fields.templateID,
            statusID=sample_status.statusID,
            title=sample_decision.title,
            userID=sample_user.userID,
            fieldValues=field_values,
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.create(db_session, payload)
        assert exc_info.value.status_code == 409
        assert "title already exists" in exc_info.value.detail

    def test_create_project_not_found(self, db_session, sample_template_with_fields, sample_status, sample_user):
        required_fields = [f for f in sample_template_with_fields.fields if f.isRequired]
        field_values = [
            DecisionFieldValueCreate(fieldID=f.fieldID, value=f"Value for {f.name}")
            for f in required_fields
        ]
        
        payload = ArchitectureDecisionCreate(
            projectID=9999,
            templateID=sample_template_with_fields.templateID,
            statusID=sample_status.statusID,
            title="Orphan Decision",
            userID=sample_user.userID,
            fieldValues=field_values,
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.create(db_session, payload)
        assert exc_info.value.status_code == 404
        assert "project not found" in exc_info.value.detail

    def test_create_template_not_found(self, db_session, sample_project, sample_status, sample_user):
        payload = ArchitectureDecisionCreate(
            projectID=sample_project.projectID,
            templateID=9999,
            statusID=sample_status.statusID,
            title="Decision Without Template",
            userID=sample_user.userID,
            fieldValues=[],
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.create(db_session, payload)
        assert exc_info.value.status_code == 404
        assert "template not found" in exc_info.value.detail

    def test_create_status_not_found(self, db_session, sample_project, sample_template_with_fields, sample_user):
        required_fields = [f for f in sample_template_with_fields.fields if f.isRequired]
        field_values = [
            DecisionFieldValueCreate(fieldID=f.fieldID, value=f"Value for {f.name}")
            for f in required_fields
        ]
        
        payload = ArchitectureDecisionCreate(
            projectID=sample_project.projectID,
            templateID=sample_template_with_fields.templateID,
            statusID=9999,
            title="Decision With Invalid Status",
            userID=sample_user.userID,
            fieldValues=field_values,
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.create(db_session, payload)
        assert exc_info.value.status_code == 404
        assert "status not found" in exc_info.value.detail

    def test_create_missing_required_fields(self, db_session, sample_project, sample_template_with_fields, sample_status, sample_user):
        payload = ArchitectureDecisionCreate(
            projectID=sample_project.projectID,
            templateID=sample_template_with_fields.templateID,
            statusID=sample_status.statusID,
            title="Decision Without Fields",
            userID=sample_user.userID,
            fieldValues=[],
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.create(db_session, payload)
        assert exc_info.value.status_code == 400
        assert "required fields missing" in exc_info.value.detail

    def test_create_empty_title(self, db_session, sample_project, sample_template_with_fields, sample_status, sample_user):
        required_fields = [f for f in sample_template_with_fields.fields if f.isRequired]
        field_values = [
            DecisionFieldValueCreate(fieldID=f.fieldID, value=f"Value for {f.name}")
            for f in required_fields
        ]
        
        payload = ArchitectureDecisionCreate(
            projectID=sample_project.projectID,
            templateID=sample_template_with_fields.templateID,
            statusID=sample_status.statusID,
            title="   ",
            userID=sample_user.userID,
            fieldValues=field_values,
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.create(db_session, payload)
        assert exc_info.value.status_code == 400
        assert "title is required" in exc_info.value.detail


class TestArchitectureDecisionServiceUpdate:
    def test_update_title_success(self, db_session, sample_decision, sample_user):
        payload = ArchitectureDecisionUpdate(
            userID=sample_user.userID,
            title="Updated Decision Title",
        )
        result = ArchitectureDecisionService.update(
            db_session, sample_decision.decisionID, payload
        )
        
        assert "message" in result
        assert "decision" in result
        assert result["decision"].title == "Updated Decision Title"

    def test_update_not_found(self, db_session, sample_user):
        payload = ArchitectureDecisionUpdate(
            userID=sample_user.userID,
            title="New Title",
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.update(db_session, 9999, payload)
        assert exc_info.value.status_code == 404

    def test_update_duplicate_title(self, db_session, sample_decision, sample_project, sample_template_with_fields, sample_status, sample_user):
        decision2 = ArchitectureDecision(
            projectID=sample_project.projectID,
            templateID=sample_template_with_fields.templateID,
            statusID=sample_status.statusID,
            title="Another Decision",
        )
        db_session.add(decision2)
        db_session.commit()

        payload = ArchitectureDecisionUpdate(
            userID=sample_user.userID,
            title="Another Decision",
        )
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.update(
                db_session, sample_decision.decisionID, payload
            )
        assert exc_info.value.status_code == 409
        assert "title already exists" in exc_info.value.detail

    def test_update_status(self, db_session, sample_decision, sample_status_2, sample_user):
        payload = ArchitectureDecisionUpdate(
            userID=sample_user.userID,
            statusID=sample_status_2.statusID,
        )
        result = ArchitectureDecisionService.update(
            db_session, sample_decision.decisionID, payload
        )
        
        assert result["decision"].statusID == sample_status_2.statusID


class TestArchitectureDecisionServiceDelete:

    def test_delete_success(self, db_session, sample_decision):
        decision_id = sample_decision.decisionID
        result = ArchitectureDecisionService.delete(db_session, decision_id)
        
        assert "message" in result
        assert "deleted successfully" in result["message"]
        
        with pytest.raises(HTTPException):
            ArchitectureDecisionService.get(db_session, decision_id)

    def test_delete_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.delete(db_session, 9999)
        assert exc_info.value.status_code == 404


class TestArchitectureDecisionServiceGetDocumentation:

    def test_get_documentation_success(self, db_session, sample_decision):
        result = ArchitectureDecisionService.get_documentation(
            db_session, sample_decision.decisionID
        )
        
        assert result.decisionID == sample_decision.decisionID
        assert result.title == sample_decision.title
        assert hasattr(result, "fields")
        assert result.templateName is not None

    def test_get_documentation_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            ArchitectureDecisionService.get_documentation(db_session, 9999)
        assert exc_info.value.status_code == 404
