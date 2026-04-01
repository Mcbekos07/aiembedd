from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_prompt_version import AIPromptVersion


class PromptVersionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_versions(self, project_id: int) -> list[AIPromptVersion]:
        stmt = select(AIPromptVersion).where(AIPromptVersion.project_id == project_id).order_by(AIPromptVersion.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def create_version(self, project_id: int, prompt_text: str) -> AIPromptVersion:
        current = self.list_versions(project_id)
        next_patch = len(current) + 1
        row = AIPromptVersion(project_id=project_id, version=f'1.0.{next_patch}', prompt_text=prompt_text)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
