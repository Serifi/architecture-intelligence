from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.features.architecture_decision.history.enum import HistoryEventType


class ArchitectureDecisionHistoryBase(BaseModel):
    decisionID: int = Field(..., ge=1)
    userID: int = Field(..., ge=1)
    fieldID: Optional[int] = None
    eventType: HistoryEventType


class ArchitectureDecisionHistoryCreate(ArchitectureDecisionHistoryBase):
    newValue: Optional[str] = None


class ArchitectureDecisionHistoryRead(BaseModel):
    historyID: int
    decisionID: int
    userID: int
    fieldID: Optional[int]
    eventType: HistoryEventType
    createdAt: datetime
    message: str

    model_config = {"from_attributes": True}