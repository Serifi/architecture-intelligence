from typing import List

from fastapi import APIRouter, Depends, Path, Query, Body, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.architecture_decision.schema import (
    ArchitectureDecisionCreate,
    ArchitectureDecisionUpdate,
    ArchitectureDecisionRead,
    ArchitectureDecisionSummaryRead,
    ArchitectureDecisionGenerateAI,
    DecisionDocumentationRead,
    ArchitectureDecisionResponse,
    MessageResponse,
    ArchitectureDecisionAISuggestion, ArchitectureDecisionCompareResponse,
    ArchitectureDecisionCompareRequest, ArchitectureDecisionChatResponse, ArchitectureDecisionChatRequest,  # <--- NEU
)
from backend.features.architecture_decision.service import (
    ArchitectureDecisionService,
)

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.get("/summaries", response_model=List[ArchitectureDecisionSummaryRead])
def list_all_decision_summaries(
    db: Session = Depends(get_db),
):
    decisions = ArchitectureDecisionService.list_all(db)
    return [
        ArchitectureDecisionSummaryRead(
            decisionID=d.decisionID,
            title=d.title,
            statusName=d.status.name if getattr(d, "status", None) else None,
            lastUpdated=d.lastUpdated,
        )
        for d in decisions
    ]


@router.get("/", response_model=List[ArchitectureDecisionRead])
def list_decisions(
    project_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.list_by_project(db, project_id)


@router.get("/{decision_id}", response_model=ArchitectureDecisionRead)
def get_decision(
    decision_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.get(db, decision_id)


@router.get("/{decision_id}/documentation", response_model=DecisionDocumentationRead)
def get_decision_documentation(
    decision_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.get_documentation(db, decision_id)


@router.post("/", response_model=ArchitectureDecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(
    payload: ArchitectureDecisionCreate = Body(...),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.create(db, payload)


@router.put("/{decision_id}", response_model=ArchitectureDecisionResponse)
def update_decision(
    decision_id: int = Path(..., ge=1),
    payload: ArchitectureDecisionUpdate = Body(...),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.update(db, decision_id, payload)


@router.delete("/{decision_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_decision(
    decision_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.delete(db, decision_id)


@router.post("/ai/suggestion", response_model=ArchitectureDecisionAISuggestion)
def generate_decision_with_ai(
    payload: ArchitectureDecisionGenerateAI = Body(...),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.generate_suggestion_with_ai(db, payload)


@router.post("/ai/alternatives", response_model=ArchitectureDecisionCompareResponse)
def generate_alternative_decisions_with_ai(
    payload: ArchitectureDecisionCompareRequest = Body(...),
    db: Session = Depends(get_db),
):
    return ArchitectureDecisionService.generate_alternatives_with_ai(db, payload)


@router.post("/ai/chat", response_model=ArchitectureDecisionChatResponse)
def chat_about_decision(
    payload: ArchitectureDecisionChatRequest = Body(...),
    db: Session = Depends(get_db),
):
    reply = ArchitectureDecisionService.chat_about_decision(db, payload)
    return ArchitectureDecisionChatResponse(reply=reply)