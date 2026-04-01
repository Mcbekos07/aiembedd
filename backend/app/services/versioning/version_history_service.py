"""Version history query service."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.version import Version


class VersionHistoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_versions(self, project_id: int) -> list[Version]:
        stmt = select(Version).where(Version.project_id == project_id).order_by(Version.created_at.desc())
        return list(self.db.scalars(stmt).all())
