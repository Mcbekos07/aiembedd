from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_memory_entry import AIMemoryEntry


class AIMemoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, project_id: int) -> list[AIMemoryEntry]:
        stmt = select(AIMemoryEntry).where(AIMemoryEntry.project_id == project_id).order_by(AIMemoryEntry.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def add(self, project_id: int, key: str, value: str) -> AIMemoryEntry:
        row = AIMemoryEntry(project_id=project_id, key=key, value=value)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def summary(self, project_id: int) -> str:
        items = self.list(project_id)[:20]
        return '\n'.join([f'{item.key}: {item.value}' for item in items])
