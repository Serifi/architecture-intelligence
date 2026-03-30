from typing import List, Optional, Dict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.features.architecture_decision.history.enum import HistoryEventType
from backend.features.architecture_decision.model import ArchitectureDecision
from backend.features.architecture_decision.status.model import Status
from backend.features.documentation_template.fields.model import DocumentationTemplateField
from backend.features.user.model import User
from backend.features.architecture_decision.history.model import ArchitectureDecisionHistory
from backend.features.architecture_decision.history.repository import DecisionHistoryRepository
from backend.features.architecture_decision.history.schema import ArchitectureDecisionHistoryCreate, ArchitectureDecisionHistoryRead


class DecisionHistoryService:
    @staticmethod
    def list_for_decision(db: Session, decision_id: int) -> List[ArchitectureDecisionHistoryRead]:
        entries = DecisionHistoryRepository.get_for_decision(db, decision_id)
        return [DecisionHistoryService._to_read_model(entry) for entry in entries]

    @staticmethod
    def add_entry(db: Session, payload: ArchitectureDecisionHistoryCreate) -> ArchitectureDecisionHistoryRead:
        message = DecisionHistoryService._build_message_for_params(
            db=db,
            decision_id=payload.decisionID,
            user_id=payload.userID,
            event_type=payload.eventType,
            field_id=payload.fieldID,
            new_value=payload.newValue,
        )
        entry = DecisionHistoryRepository.add_entry(
            db,
            decision_id=payload.decisionID,
            user_id=payload.userID,
            event_type=payload.eventType,
            field_id=payload.fieldID,
            message=message,
        )
        return DecisionHistoryService._to_read_model(entry)

    @staticmethod
    def delete(db: Session, history_id: int):
        entry = db.get(ArchitectureDecisionHistory, history_id)
        if entry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History entry not found.",
            )
        DecisionHistoryRepository.delete(db, history_id)
        return {"message": "History entry was deleted successfully."}

    @staticmethod
    def add_created_entry(db: Session, decision_id: int, user_id: int):
        message = DecisionHistoryService._build_message_for_params(
            db=db,
            decision_id=decision_id,
            user_id=user_id,
            event_type=HistoryEventType.CREATED,
            field_id=None,
            new_value=None,
        )
        DecisionHistoryRepository.add_entry(
            db,
            decision_id=decision_id,
            user_id=user_id,
            event_type=HistoryEventType.CREATED,
            field_id=None,
            message=message,
        )

    @staticmethod
    def add_status_change_entry(db: Session, decision_id: int, user_id: int):
        message = DecisionHistoryService._build_message_for_params(
            db=db,
            decision_id=decision_id,
            user_id=user_id,
            event_type=HistoryEventType.STATUS_CHANGED,
            field_id=None,
            new_value=None,
        )
        DecisionHistoryRepository.add_entry(
            db,
            decision_id=decision_id,
            user_id=user_id,
            event_type=HistoryEventType.STATUS_CHANGED,
            field_id=None,
            message=message,
        )

    @staticmethod
    def add_field_change_entries(
        db: Session,
        decision_id: int,
        changed_fields: Dict[int, Optional[str]],
        user_id: int,
    ):
        for field_id, new_value in changed_fields.items():
            message = DecisionHistoryService._build_message_for_params(
                db=db,
                decision_id=decision_id,
                user_id=user_id,
                event_type=HistoryEventType.FIELD_CHANGED,
                field_id=field_id,
                new_value=new_value,
            )
            DecisionHistoryRepository.add_entry(
                db,
                decision_id=decision_id,
                user_id=user_id,
                event_type=HistoryEventType.FIELD_CHANGED,
                field_id=field_id,
                message=message,
            )

    @staticmethod
    def _to_read_model(entry: ArchitectureDecisionHistory) -> ArchitectureDecisionHistoryRead:
        return ArchitectureDecisionHistoryRead(
            historyID=entry.historyID,
            decisionID=entry.decisionID,
            userID=entry.userID,
            fieldID=entry.fieldID,
            eventType=entry.eventType,
            createdAt=entry.createdAt,
            message=entry.message,
        )

    @staticmethod
    def _build_message_for_params(
        db: Session,
        decision_id: int,
        user_id: int,
        event_type: HistoryEventType,
        field_id: Optional[int],
        new_value: Optional[str],
    ) -> str:
        decision = db.get(ArchitectureDecision, decision_id)
        title = decision.title if decision else f"Architecture Decision {decision_id}"

        user = db.get(User, user_id)
        user_label = user.email if user else f"User {user_id}"

        if event_type == HistoryEventType.CREATED:
            return f"User '{user_label}' created Architecture Decision '{title}'."

        if event_type == HistoryEventType.STATUS_CHANGED:
            if decision and decision.statusID is not None:
                status_obj = db.get(Status, decision.statusID)
                status_name = status_obj.name if status_obj else f"Status {decision.statusID}"
                return (
                    f"User '{user_label}' changed status of Architecture Decision "
                    f"'{title}' to '{status_name}'."
                )
            return f"User '{user_label}' changed status of Architecture Decision '{title}'."

        if event_type == HistoryEventType.FIELD_CHANGED:
            field_name = f"Field {field_id}"
            if field_id is not None:
                field = db.get(DocumentationTemplateField, field_id)
                if field:
                    field_name = field.name
            if new_value is not None and str(new_value).strip() != "":
                return (
                    f"User '{user_label}' changed field '{field_name}' of "
                    f"Architecture Decision '{title}' to '{new_value}'."
                )
            return (
                f"User '{user_label}' changed field '{field_name}' of "
                f"Architecture Decision '{title}'."
            )

        return f"User '{user_label}' updated Architecture Decision '{title}'."