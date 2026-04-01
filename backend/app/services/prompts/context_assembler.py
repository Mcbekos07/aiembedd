from sqlalchemy.orm import Session

from app.services.ai.ai_log_context_service import AILogContextService
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.build.build_service import BuildService
from app.services.git.git_diff_service import GitDiffService
from app.services.prompts.context_budget_service import ContextBudgetService


class ContextAssembler:
    def __init__(self, db: Session) -> None:
        self.db = db

    def assemble(self, project_id: int, repo_path: str, user_input: str) -> str:
        memory = AIMemoryService(self.db).summary(project_id)
        diff = ''
        try:
            diff = GitDiffService().diff(repo_path)
        except Exception:
            diff = 'diff unavailable'
        recent_jobs = BuildService(self.db).list_jobs(project_id)[:1]
        build_summary = recent_jobs[0].error_summary if recent_jobs else 'нет build summary'
        logs = AILogContextService().extract(build_summary)
        return ContextBudgetService().trim([
            f'user_input: {user_input}',
            f'memory: {memory}',
            f'diff: {diff}',
            f'build_summary: {build_summary}',
            f'important_logs: {logs}',
        ])
