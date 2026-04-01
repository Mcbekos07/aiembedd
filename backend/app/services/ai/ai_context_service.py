from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.services.prompts.context_assembler import ContextAssembler


class AIContextService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def build_context(self, project: Project, user_input: str) -> str:
        return ContextAssembler(self.db).assemble(project.id, project.path, user_input)
