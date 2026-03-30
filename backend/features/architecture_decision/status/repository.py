from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.features.architecture_decision.status.model import Status
from backend.features.architecture_decision.model import ArchitectureDecision


class StatusRepository:
    @staticmethod
    def get_all(db: Session) -> List[Status]:
        stmt = select(Status).order_by(Status.position, Status.statusID)
        return db.execute(stmt).scalars().all()

    @staticmethod
    def get_by_id(db: Session, status_id: int) -> Optional[Status]:
        return db.get(Status, status_id)

    @staticmethod
    def exists_by_name(db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
        q = db.query(Status).filter(func.lower(Status.name) == func.lower(name))
        if exclude_id is not None:
            q = q.filter(Status.statusID != exclude_id)
        return db.query(q.exists()).scalar()

    @staticmethod
    def exists_by_position(db: Session, position: int, exclude_id: Optional[int] = None) -> bool:
        q = db.query(Status).filter(Status.position == position)
        if exclude_id is not None:
            q = q.filter(Status.statusID != exclude_id)
        return db.query(q.exists()).scalar()

    @staticmethod
    def create(db: Session, name: str, color: str, position: int) -> Status:
        status = Status(name=name, color=color, position=position)
        db.add(status)
        db.commit()
        db.refresh(status)
        return status

    @staticmethod
    def update(db: Session, status: Status, name: Optional[str], color: Optional[str], position: Optional[int]) -> Status:
        if name is not None:
            status.name = name
        if color is not None:
            status.color = color

        if position is not None:
            all_statuses: List[Status] = (
                db.query(Status)
                .order_by(Status.position, Status.statusID)
                .all()
            )

            cleaned = [s for s in all_statuses if s.statusID != status.statusID]

            target_index = position
            if target_index < 0:
                target_index = 0
            if target_index > len(cleaned):
                target_index = len(cleaned)

            cleaned.insert(target_index, status)

            max_pos = db.query(func.max(Status.position)).scalar() or 0
            bump = max_pos + 1000

            for s in cleaned:
                s.position += bump
            db.flush()

            for idx, s in enumerate(cleaned):
                s.position = idx

        db.commit()
        db.refresh(status)
        return status

    @staticmethod
    def delete(db: Session, status: Status) -> None:
        db.delete(status)
        db.commit()

    @staticmethod
    def reassign_decisions(db: Session, from_status_id: int, to_status_id: int) -> None:
        db.query(ArchitectureDecision).filter(
            ArchitectureDecision.statusID == from_status_id
        ).update(
            {ArchitectureDecision.statusID: to_status_id},
            synchronize_session=False,
        )
        db.commit()

    @staticmethod
    def reorder(db: Session, items: List[tuple[int, int]]) -> List[Status]:
        statuses = {s.statusID: s for s in db.query(Status).all()}

        max_pos = db.query(func.max(Status.position)).scalar() or 0
        bump = max_pos + 1000

        for sid, _ in items:
            statuses[sid].position += bump
        db.flush()

        for sid, pos in items:
            statuses[sid].position = pos

        db.commit()
        return StatusRepository.get_all(db)

    @staticmethod
    def shift_positions_from(db: Session, start_pos: int):
        max_pos = db.query(func.max(Status.position)).scalar() or 0

        bump = max_pos + 1000

        db.query(Status).filter(Status.position >= start_pos).update(
            {Status.position: Status.position + bump},
            synchronize_session=False,
        )

        db.flush()