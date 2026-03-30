from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.features.architecture_decision.history.model import ArchitectureDecisionHistory
from backend.features.architecture_decision.history.enum import HistoryEventType


class DecisionHistoryRepository:
    @staticmethod
    def get_for_decision(db: Session, decision_id: int) -> List[ArchitectureDecisionHistory]:
        stmt = (
            select(ArchitectureDecisionHistory)
            .where(ArchitectureDecisionHistory.decisionID == decision_id)
            .order_by(ArchitectureDecisionHistory.createdAt.desc())
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def add_entry(db: Session, decision_id: int, user_id: int, event_type: HistoryEventType, field_id: Optional[int], message: str) -> ArchitectureDecisionHistory:
        entry = ArchitectureDecisionHistory(
            decisionID=decision_id,
            userID=user_id,
            fieldID=field_id,
            eventType=event_type,
            message=message,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete(db: Session, history_id: int) -> Optional[ArchitectureDecisionHistory]:
        entry = db.get(ArchitectureDecisionHistory, history_id)
        if entry is None:
            return None
        db.delete(entry)
        db.commit()
        return entry