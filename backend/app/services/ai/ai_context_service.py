from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.services.context.context_pipeline_service import ContextPipelineService


class AIContextService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def build_context(self, project: Project, user_input: str, mode: str = 'quick_diagnosis') -> str:
        result = ContextPipelineService(self.db).build(project, task_text=user_input, mode=mode)
        return str(result['prompt_text'])

    def build_context_with_report(self, project: Project, user_input: str, mode: str = 'quick_diagnosis') -> dict[str, object]:
        return ContextPipelineService(self.db).build(project, task_text=user_input, mode=mode)

    def build_diagnosis_context(
        self,
        project: Project,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        task_text: str = '',
        mode: str = 'deep_build_fix',
    ) -> str:
        result = ContextPipelineService(self.db).build(
            project,
            task_text=task_text,
            mode=mode,
            opened_file_path=opened_file_path,
            opened_file_content=opened_file_content,
        )
        return str(result['prompt_text'])

    def build_diagnosis_with_report(
        self,
        project: Project,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        task_text: str = '',
        mode: str = 'deep_build_fix',
    ) -> dict[str, object]:
        return ContextPipelineService(self.db).build(
            project,
            task_text=task_text,
            mode=mode,
            opened_file_path=opened_file_path,
            opened_file_content=opened_file_content,
        )
