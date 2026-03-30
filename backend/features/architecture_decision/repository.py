from datetime import datetime, timezone
from typing import List, Optional, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.features.architecture_decision.model import ArchitectureDecision
from backend.features.architecture_decision.fields.model import ArchitectureDecisionFieldValue
from backend.features.documentation_template.model import DocumentationTemplate
from backend.features.architecture_decision.schema import DecisionFieldValueCreate


class ArchitectureDecisionRepository:
    @staticmethod
    def get_by_id(db: Session, decision_id: int) -> Optional[ArchitectureDecision]:
        return db.get(ArchitectureDecision, decision_id)

    @staticmethod
    def list_by_project(db: Session, project_id: int) -> List[ArchitectureDecision]:
        stmt = select(ArchitectureDecision).where(
            ArchitectureDecision.projectID == project_id
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def create(db: Session, project_id: int, template_id: int, status_id: Optional[int], title: str, field_values: List[DecisionFieldValueCreate]) -> ArchitectureDecision:
        decision = ArchitectureDecision(
            projectID=project_id,
            templateID=template_id,
            statusID=status_id,
            title=title
        )
        db.add(decision)
        db.flush()

        for fv in field_values:
            db.add(
                ArchitectureDecisionFieldValue(
                    decisionID=decision.decisionID,
                    fieldID=fv.fieldID,
                    value=fv.value,
                )
            )

        db.commit()
        db.refresh(decision)
        return decision

    @staticmethod
    def update(db: Session, decision: ArchitectureDecision, template_id: Optional[int], status_id: Optional[int], title: Optional[str], field_values: Optional[List[DecisionFieldValueCreate]]) -> ArchitectureDecision:
        if template_id is not None:
            decision.templateID = template_id
        if status_id is not None:
            decision.statusID = status_id
        if title is not None:
            decision.title = title

        if field_values is not None:
            existing: Dict[int, ArchitectureDecisionFieldValue] = {
                fv.fieldID: fv
                for fv in db.query(ArchitectureDecisionFieldValue)
                .filter(ArchitectureDecisionFieldValue.decisionID == decision.decisionID)
                .all()
            }

            for fv in field_values:
                if fv.fieldID in existing:
                    existing[fv.fieldID].value = fv.value
                else:
                    db.add(
                        ArchitectureDecisionFieldValue(
                            decisionID=decision.decisionID,
                            fieldID=fv.fieldID,
                            value=fv.value,
                        )
                    )

        decision.lastUpdated = datetime.now(timezone.utc)

        db.commit()
        db.refresh(decision)
        return decision

    @staticmethod
    def delete(db: Session, decision: ArchitectureDecision) -> None:
        db.delete(decision)
        db.commit()

    @staticmethod
    def list_all(db: Session) -> List[ArchitectureDecision]:
        stmt = select(ArchitectureDecision).order_by(ArchitectureDecision.decisionID)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_with_template_and_values(db: Session, decision_id: int) -> Optional[ArchitectureDecision]:
        stmt = (
            select(ArchitectureDecision)
            .options(
                joinedload(ArchitectureDecision.template).joinedload(
                    DocumentationTemplate.fields
                ),
                joinedload(ArchitectureDecision.fieldValues),
            )
            .where(ArchitectureDecision.decisionID == decision_id)
        )
        return db.execute(stmt).scalars().first()