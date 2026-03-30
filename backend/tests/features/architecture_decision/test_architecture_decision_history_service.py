import pytest
from fastapi import HTTPException

from backend.features.architecture_decision.history.service import DecisionHistoryService
from backend.features.architecture_decision.history.schema import ArchitectureDecisionHistoryCreate
from backend.features.architecture_decision.history.enum import HistoryEventType


class TestDecisionHistoryServiceListForDecision:

    def test_list_for_decision_empty(self, db_session, sample_decision):
        result = DecisionHistoryService.list_for_decision(
            db_session, sample_decision.decisionID
        )
        assert isinstance(result, list)

    def test_list_for_decision_with_data(self, db_session, sample_decision, sample_user):
        DecisionHistoryService.add_created_entry(
            db_session, sample_decision.decisionID, sample_user.userID
        )
        
        result = DecisionHistoryService.list_for_decision(
            db_session, sample_decision.decisionID
        )
        assert len(result) >= 1


class TestDecisionHistoryServiceAddEntry:

    def test_add_entry_created(self, db_session, sample_decision, sample_user):
        payload = ArchitectureDecisionHistoryCreate(
            decisionID=sample_decision.decisionID,
            userID=sample_user.userID,
            eventType=HistoryEventType.CREATED,
        )
        result = DecisionHistoryService.add_entry(db_session, payload)
        
        assert result.decisionID == sample_decision.decisionID
        assert result.eventType == HistoryEventType.CREATED
        assert result.message is not None

    def test_add_entry_status_changed(self, db_session, sample_decision, sample_user):
        payload = ArchitectureDecisionHistoryCreate(
            decisionID=sample_decision.decisionID,
            userID=sample_user.userID,
            eventType=HistoryEventType.STATUS_CHANGED,
        )
        result = DecisionHistoryService.add_entry(db_session, payload)
        
        assert result.decisionID == sample_decision.decisionID
        assert result.eventType == HistoryEventType.STATUS_CHANGED

    def test_add_entry_field_changed(self, db_session, sample_decision, sample_user, sample_template_with_fields):
        field = sample_template_with_fields.fields[0]
        payload = ArchitectureDecisionHistoryCreate(
            decisionID=sample_decision.decisionID,
            userID=sample_user.userID,
            eventType=HistoryEventType.FIELD_CHANGED,
            fieldID=field.fieldID,
            newValue="New value",
        )
        result = DecisionHistoryService.add_entry(db_session, payload)
        
        assert result.decisionID == sample_decision.decisionID
        assert result.eventType == HistoryEventType.FIELD_CHANGED


class TestDecisionHistoryServiceDelete:

    def test_delete_success(self, db_session, sample_decision, sample_user):
        payload = ArchitectureDecisionHistoryCreate(
            decisionID=sample_decision.decisionID,
            userID=sample_user.userID,
            eventType=HistoryEventType.CREATED,
        )
        entry = DecisionHistoryService.add_entry(db_session, payload)
        
        result = DecisionHistoryService.delete(db_session, entry.historyID)
        assert "message" in result
        assert "deleted successfully" in result["message"]

    def test_delete_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            DecisionHistoryService.delete(db_session, 9999)
        assert exc_info.value.status_code == 404
        assert "History entry not found" in exc_info.value.detail


class TestDecisionHistoryServiceAddCreatedEntry:

    def test_add_created_entry(self, db_session, sample_decision, sample_user):
        DecisionHistoryService.add_created_entry(
            db_session, sample_decision.decisionID, sample_user.userID
        )
        
        entries = DecisionHistoryService.list_for_decision(
            db_session, sample_decision.decisionID
        )
        created_entries = [e for e in entries if e.eventType == HistoryEventType.CREATED]
        assert len(created_entries) >= 1
        assert "created" in created_entries[-1].message.lower()


class TestDecisionHistoryServiceAddStatusChangeEntry:

    def test_add_status_change_entry(self, db_session, sample_decision, sample_user):
        DecisionHistoryService.add_status_change_entry(
            db_session, sample_decision.decisionID, sample_user.userID
        )
        
        entries = DecisionHistoryService.list_for_decision(
            db_session, sample_decision.decisionID
        )
        status_entries = [e for e in entries if e.eventType == HistoryEventType.STATUS_CHANGED]
        assert len(status_entries) >= 1


class TestDecisionHistoryServiceAddFieldChangeEntries:

    def test_add_field_change_entries(self, db_session, sample_decision, sample_user, sample_template_with_fields):
        field1 = sample_template_with_fields.fields[0]
        field2 = sample_template_with_fields.fields[1]
        
        changed_fields = {
            field1.fieldID: "New value 1",
            field2.fieldID: "New value 2",
        }
        
        DecisionHistoryService.add_field_change_entries(
            db_session, sample_decision.decisionID, changed_fields, sample_user.userID
        )
        
        entries = DecisionHistoryService.list_for_decision(
            db_session, sample_decision.decisionID
        )
        field_entries = [e for e in entries if e.eventType == HistoryEventType.FIELD_CHANGED]
        assert len(field_entries) >= 2
