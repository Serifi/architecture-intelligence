from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, Field


class DecisionFieldValueBase(BaseModel):
    fieldID: int = Field(..., ge=1)
    value: Optional[str] = None


class DecisionFieldValueCreate(DecisionFieldValueBase):
    pass


class DecisionFieldValueRead(DecisionFieldValueBase):
    pass


class ArchitectureDecisionBase(BaseModel):
    projectID: int = Field(..., ge=1)
    templateID: int = Field(..., ge=1)
    statusID: Optional[int] = Field(None, ge=1)
    title: str = Field(..., min_length=1, max_length=255)


class ArchitectureDecisionCreate(ArchitectureDecisionBase):
    userID: int = Field(..., ge=1)
    fieldValues: List[DecisionFieldValueCreate] = []


class ArchitectureDecisionUpdate(BaseModel):
    userID: int = Field(..., ge=1)
    templateID: Optional[int] = Field(None, ge=1)
    statusID: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    fieldValues: Optional[List[DecisionFieldValueCreate]] = None


class ArchitectureDecisionRead(ArchitectureDecisionBase):
    decisionID: int
    createdAt: datetime
    lastUpdated: datetime
    fieldValues: List[DecisionFieldValueRead] = []

    model_config = {"from_attributes": True}


class ArchitectureDecisionSummaryRead(BaseModel):
    decisionID: int
    title: str
    statusName: Optional[str] = None
    lastUpdated: datetime

    model_config = {"from_attributes": True}


class DecisionDocumentationField(BaseModel):
    fieldID: int
    name: str
    isRequired: bool
    value: Optional[str] = None


class DecisionDocumentationRead(BaseModel):
    decisionID: int
    projectID: int
    statusID: Optional[int]
    title: str
    templateID: int
    templateName: str
    fields: List[DecisionDocumentationField]


class ArchitectureDecisionResponse(BaseModel):
    message: str
    decision: ArchitectureDecisionRead


class MessageResponse(BaseModel):
    message: str


class ArchitectureDecisionGenerateAI(BaseModel):
    projectID: int
    templateID: int
    prompt: str


class ArchitectureDecisionAISuggestionField(BaseModel):
    fieldID: int
    name: str
    isRequired: bool
    value: Optional[str] = None


class ArchitectureDecisionAISuggestion(BaseModel):
    title: str
    statusName: Optional[str] = None
    fields: List[ArchitectureDecisionAISuggestionField]

class ArchitectureDecisionAlternative(BaseModel):
    title: str
    statusName: Optional[str] = None
    fields: List[ArchitectureDecisionAISuggestionField]


class ArchitectureDecisionCompareRequest(BaseModel):
    projectID: int
    templateID: int
    prompt: str
    base: ArchitectureDecisionAISuggestion
    numberOfAlternatives: int = Field(2, ge=1, le=5)


class ArchitectureDecisionCompareResponse(BaseModel):
    base: ArchitectureDecisionAISuggestion
    alternatives: List[ArchitectureDecisionAlternative]
    comparisonSummary: str


class ArchitectureDecisionChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ArchitectureDecisionChatRequest(BaseModel):
    projectID: int
    suggestion: Optional[ArchitectureDecisionAISuggestion] = None
    messages: List[ArchitectureDecisionChatMessage]


class ArchitectureDecisionChatResponse(BaseModel):
    reply: str