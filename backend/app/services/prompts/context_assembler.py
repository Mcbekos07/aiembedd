from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.services.ai.ai_log_context_service import AILogContextService
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.build.build_service import BuildService
from app.services.context.project_context_retrieval_service import ProjectContextRetrievalService
from app.services.git.git_diff_service import GitDiffService
from app.services.git.git_service import GitService
from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService
from app.services.project.project_intelligence_service import ProjectIntelligenceService
from app.services.prompts.context_budget_service import ContextBudgetService
from app.services.prompts.prompt_packer_service import PromptPackerService
from app.services.prompts.prompt_service import PromptService


class ContextAssembler:
    def __init__(self, db: Session) -> None:
        self.db = db

    def assemble(self, project_id: int, repo_path: str, user_input: str, mode: str = 'quick_diagnosis') -> str:
        memory_service = AIMemoryService(self.db)
        layers = memory_service.get_memory_layers(project_id, task_text=user_input, include_cold=False)
        diff = ''
        try:
            diff = GitDiffService().diff(repo_path)
        except Exception:
            diff = 'diff unavailable'
        recent_jobs = BuildService(self.db).list_jobs(project_id)[:1]
        build_summary = recent_jobs[0].error_summary if recent_jobs else 'нет build summary'
        logs = AILogContextService().extract(build_summary)

        fragments = [
            {'id': 'task', 'category': 'task_instruction', 'title': 'user_task', 'content': user_input, 'rank': 100},
            {'id': 'critical_logs', 'category': 'critical_log', 'title': 'build_runtime_logs', 'content': logs, 'rank': 95},
            {'id': 'active_memory', 'category': 'active_memory', 'title': 'active_memory', 'content': str(layers['active']), 'rank': 85},
            {'id': 'warm_memory', 'category': 'warm_memory', 'title': 'warm_memory', 'content': str(layers['warm']), 'rank': 65},
            {'id': 'git_diff', 'category': 'git_history', 'title': 'git_diff', 'content': diff, 'rank': 55},
        ]
        system_prompt = PromptService(self.db).get_current_prompt(project_id)
        packed = PromptPackerService().pack(mode=mode, system_prompt=system_prompt, task_text=user_input, fragments=fragments)
        prompt_text = str(packed['final_context_payload']['prompt_text'])
        return ContextBudgetService().trim([prompt_text], max_chars=24000)

    def assemble_diagnosis(
        self,
        project: Project,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        task_text: str = '',
        mode: str = 'deep_build_fix',
    ) -> str:
        snapshot = ProjectIntelligenceService(self.db).get_or_refresh(project, refresh=False)
        jobs = BuildService(self.db).list_jobs(project.id)
        failed_jobs = [j for j in jobs if j.status == 'failed'][:3]

        latest_failed_summary = failed_jobs[0].error_summary if failed_jobs else ''
        critical_events: list[dict[str, object]] = []
        if failed_jobs:
            latest = failed_jobs[0]
            try:
                raw = Path(latest.log_path).read_text(encoding='utf-8')
            except Exception:
                raw = ''
            events = ImportantLogService().extract_events(raw)
            critical_events = [e for e in events if str(e.get('severity')) == 'critical'][:12]

        diff = ''
        status = ''
        try:
            diff = GitDiffService().diff(project.path)[:3000]
            status = GitService().run(project.path, ['status', '--short'])
        except Exception:
            diff = 'diff unavailable'
            status = 'status unavailable'

        retrieval = ProjectContextRetrievalService(self.db).retrieve(
            project,
            task_text=task_text,
            opened_file_path=opened_file_path,
            opened_file_content=opened_file_content,
            max_files=8,
            max_fragments=6,
            max_memory=6,
            max_history=6,
        )

        compressed_logs = LogSummaryService().compress(raw if failed_jobs else '', critical_events)
        summary_obj = compressed_logs.get('root_cause_summary', {})
        ai_log_context = str(compressed_logs.get('compressed_ai_context', ''))

        active_memory = AIMemoryService(self.db).get_active_memory_for_task(project.id, task_text=task_text, opened_file_path=opened_file_path)
        warm_memory = AIMemoryService(self.db).get_relevant_warm_memory(project.id, task_text=task_text, opened_file_path=opened_file_path)

        fragments: list[dict[str, object]] = [
            {'id': 'task', 'category': 'task_instruction', 'title': 'diagnosis_task', 'content': task_text, 'rank': 100},
            {'id': 'critical_logs', 'category': 'critical_log', 'title': 'critical_log_context', 'content': ai_log_context, 'rank': 97},
            {'id': 'build_summary', 'category': 'critical_log', 'title': 'build_summary', 'content': str(summary_obj), 'rank': 94},
        ]

        for idx, item in enumerate(retrieval.fragments[:6]):
            fragments.append(
                {
                    'id': f'code_{idx}',
                    'category': 'code_fragment',
                    'title': item.path,
                    'path': item.path,
                    'content': item.snippet,
                    'rank': item.score.total,
                }
            )

        fragments.append({'id': 'active_memory', 'category': 'active_memory', 'title': 'active_memory', 'content': str(active_memory), 'rank': 88})
        fragments.append({'id': 'warm_memory', 'category': 'warm_memory', 'title': 'warm_memory', 'content': str(warm_memory), 'rank': 66})
        fragments.append({'id': 'git_status', 'category': 'git_history', 'title': 'git_status', 'content': status, 'rank': 58})
        fragments.append({'id': 'git_diff', 'category': 'git_history', 'title': 'git_diff', 'content': diff, 'rank': 56})
        fragments.append({'id': 'project_notes', 'category': 'warm_memory', 'title': 'project_notes', 'content': snapshot.architectural_notes, 'rank': 60})
        fragments.append({'id': 'failed_build_summary', 'category': 'critical_log', 'title': 'failed_build_summary', 'content': latest_failed_summary, 'rank': 92})

        system_prompt = PromptService(self.db).get_current_prompt(project.id)
        packed = PromptPackerService().pack(mode=mode, system_prompt=system_prompt, task_text=task_text, fragments=fragments)
        prompt_text = str(packed['final_context_payload']['prompt_text'])
        return ContextBudgetService().trim([prompt_text], max_chars=24000)
