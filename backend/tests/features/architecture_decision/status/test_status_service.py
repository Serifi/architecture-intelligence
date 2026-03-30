import pytest
from fastapi import HTTPException

from backend.features.architecture_decision.status.service import StatusService
from backend.features.architecture_decision.status.schema import StatusCreate, StatusUpdate, StatusReorderItem


class TestStatusServiceListStatuses:

    def test_list_statuses_empty(self, db_session):
        result = StatusService.list_statuses(db_session)
        assert result == []

    def test_list_statuses_with_data(self, db_session, sample_status):
        result = StatusService.list_statuses(db_session)
        assert len(result) == 1
        assert result[0].name == sample_status.name


class TestStatusServiceGetStatus:

    def test_get_status_success(self, db_session, sample_status):
        result = StatusService.get_status(db_session, sample_status.statusID)
        assert result.statusID == sample_status.statusID
        assert result.name == sample_status.name

    def test_get_status_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            StatusService.get_status(db_session, 9999)
        assert exc_info.value.status_code == 404
        assert "Status not found" in exc_info.value.detail


class TestStatusServiceCreateStatus:

    def test_create_status_success(self, db_session):
        payload = StatusCreate(
            name="In Progress",
            color="#FFA500",
            position=0,
        )
        result = StatusService.create_status(db_session, payload)
        
        assert "message" in result
        assert "status" in result
        assert result["status"].name == "In Progress"
        assert result["status"].color == "#FFA500"

    def test_create_status_duplicate_name(self, db_session, sample_status):
        payload = StatusCreate(
            name=sample_status.name,
            color="#FF0000",
            position=1,
        )
        with pytest.raises(HTTPException) as exc_info:
            StatusService.create_status(db_session, payload)
        assert exc_info.value.status_code == 409
        assert "name already exists" in exc_info.value.detail


class TestStatusServiceUpdateStatus:

    def test_update_status_success(self, db_session, sample_status):
        payload = StatusUpdate(
            name="Updated Status",
            color="#00FF00",
            position=5,
        )
        result = StatusService.update_status(db_session, sample_status.statusID, payload)
        
        assert "message" in result
        assert "status" in result
        assert result["status"].name == "Updated Status"
        assert result["status"].color == "#00FF00"

    def test_update_status_not_found(self, db_session):
        payload = StatusUpdate(name="New Name", color="#000000", position=0)
        with pytest.raises(HTTPException) as exc_info:
            StatusService.update_status(db_session, 9999, payload)
        assert exc_info.value.status_code == 404

    def test_update_status_no_fields(self, db_session, sample_status):
        payload = StatusUpdate()
        with pytest.raises(HTTPException) as exc_info:
            StatusService.update_status(db_session, sample_status.statusID, payload)
        assert exc_info.value.status_code == 400
        assert "at least one field" in exc_info.value.detail

    def test_update_status_duplicate_name(self, db_session, sample_status, sample_status_2):
        payload = StatusUpdate(name=sample_status_2.name)
        with pytest.raises(HTTPException) as exc_info:
            StatusService.update_status(db_session, sample_status.statusID, payload)
        assert exc_info.value.status_code == 409
        assert "name already exists" in exc_info.value.detail


class TestStatusServiceDeleteStatus:

    def test_delete_status_success(self, db_session, sample_status):
        status_id = sample_status.statusID
        result = StatusService.delete_status(db_session, status_id)
        
        assert "message" in result
        assert "deleted" in result
        assert result["deleted"] is True

    def test_delete_status_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            StatusService.delete_status(db_session, 9999)
        assert exc_info.value.status_code == 404


class TestStatusServiceReorderStatuses:

    def test_reorder_statuses_success(self, db_session, sample_status, sample_status_2):
        items = [
            StatusReorderItem(statusID=sample_status_2.statusID, position=0),
            StatusReorderItem(statusID=sample_status.statusID, position=1),
        ]
        result = StatusService.reorder_statuses(db_session, items)
        
        assert "message" in result
        assert "reordered successfully" in result["message"]

    def test_reorder_statuses_empty_payload(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            StatusService.reorder_statuses(db_session, [])
        assert exc_info.value.status_code == 400
        assert "must not be empty" in exc_info.value.detail

    def test_reorder_statuses_duplicate_ids(self, db_session, sample_status):
        items = [
            StatusReorderItem(statusID=sample_status.statusID, position=0),
            StatusReorderItem(statusID=sample_status.statusID, position=1),
        ]
        with pytest.raises(HTTPException) as exc_info:
            StatusService.reorder_statuses(db_session, items)
        assert exc_info.value.status_code == 400
        assert "Duplicate status IDs" in exc_info.value.detail

    def test_reorder_statuses_duplicate_positions(self, db_session, sample_status, sample_status_2):
        items = [
            StatusReorderItem(statusID=sample_status.statusID, position=0),
            StatusReorderItem(statusID=sample_status_2.statusID, position=0),
        ]
        with pytest.raises(HTTPException) as exc_info:
            StatusService.reorder_statuses(db_session, items)
        assert exc_info.value.status_code == 409
        assert "Duplicate positions" in exc_info.value.detail

    def test_reorder_statuses_not_found(self, db_session, sample_status):
        items = [
            StatusReorderItem(statusID=sample_status.statusID, position=0),
            StatusReorderItem(statusID=9999, position=1),
        ]
        with pytest.raises(HTTPException) as exc_info:
            StatusService.reorder_statuses(db_session, items)
        assert exc_info.value.status_code == 404
        assert "Statuses not found" in exc_info.value.detail
