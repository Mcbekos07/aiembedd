from sqlalchemy.orm import Session

from app.core.extension_points import PROMPT_TEMPLATE_KEYS
from app.services.prompts.prompt_version_service import PromptVersionService


class PromptService:
    """Manages project prompt versions and default prompt templates."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.versions = PromptVersionService(db)

    def get_current_prompt(self, project_id: int) -> str:
        versions = self.versions.list_versions(project_id)
        return versions[0].prompt_text if versions else 'Вы ассистент embedded IDE. Работай безопасно и лаконично.'

    def save_prompt(self, project_id: int, prompt_text: str):
        return self.versions.create_version(project_id, prompt_text)

    def template_keys(self) -> tuple[str, ...]:
        return PROMPT_TEMPLATE_KEYS
