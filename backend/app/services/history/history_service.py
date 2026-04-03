"""Project history read service."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.project_history import ProjectHistory


class HistoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_events(self, project_id: int) -> list[ProjectHistory]:
        stmt = select(ProjectHistory).where(ProjectHistory.project_id == project_id).order_by(ProjectHistory.created_at.desc())
        return list(self.db.scalars(stmt).all())
