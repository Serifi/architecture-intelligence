from typing import List

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.architecture_decision.history.schema import ArchitectureDecisionHistoryRead
from backend.features.architecture_decision.history.service import DecisionHistoryService

router = APIRouter(prefix="/decision-history", tags=["decision-history"])


@router.get("/", response_model=List[ArchitectureDecisionHistoryRead])
def list_history_for_decision(
    decision_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return DecisionHistoryService.list_for_decision(db, decision_id)


@router.delete("/{history_id}", status_code=status.HTTP_200_OK)
def delete_history_entry(
    history_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return DecisionHistoryService.delete(db, history_id)