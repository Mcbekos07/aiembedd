"""Service for writing timeline events."""

from sqlalchemy.orm import Session

from app.db.models.project_history import ProjectHistory


class EventWriteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def write(self, project_id: int, event_type: str, title: str, details: str = '') -> ProjectHistory:
        event = ProjectHistory(
            project_id=project_id,
            event_type=event_type,
            title=title,
            details=details,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
