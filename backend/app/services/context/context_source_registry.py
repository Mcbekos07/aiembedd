from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.monitor_session import MonitorSession
from app.db.models.project import Project
from app.schemas.context_source import ContextSourceFragment, ContextSourceMeta
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.ai.ai_task_service import AITaskService
from app.services.build.build_service import BuildService
from app.services.context.project_context_retrieval_service import ProjectContextRetrievalService
from app.services.dependencies.dependency_check_service import DependencyCheckService
from app.services.git.git_diff_service import GitDiffService
from app.services.git.git_service import GitService
from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService
from app.services.monitor.serial_monitor_service import SerialMonitorService
from app.services.project.project_intelligence_service import ProjectIntelligenceService
from app.services.prompts.prompt_service import PromptService
from app.services.prompts.prompt_version_service import PromptVersionService
from app.services.toolchains.detection_service import ToolchainDetectionService


class ContextSourceRegistry:
    DEFAULT_PRIORITIES = {
        'project_metadata': 100,
        'project_intelligence_summary': 95,
        'important_files': 92,
        'open_selected_file': 98,
        'recent_changed_files': 90,
        'git_diff_status': 88,
        'recent_commits': 82,
        'build_summary': 91,
        'important_build_logs': 93,
        'important_runtime_logs': 93,
        'project_memory': 96,
        'prompt_memory': 75,
        'recent_agent_tasks': 87,
        'dependency_toolchain_status': 70,
        'retrieval_top_files': 99,
        'retrieval_top_fragments': 99,
        'retrieval_top_memory': 97,
        'retrieval_top_history': 89,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_available_sources(self, project: Project, opened_file_path: str | None = None, opened_file_content: str | None = None) -> list[ContextSourceMeta]:
        fragments = self.fetch_source_fragments(project, opened_file_path=opened_file_path, opened_file_content=opened_file_content)
        return [item.metadata for item in fragments]

    def fetch_source_fragments(
        self,
        project: Project,
        *,
        source_types: list[str] | None = None,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        max_items_per_source: int = 5,
        task_text: str = '',
    ) -> list[ContextSourceFragment]:
        requested = set(source_types or [])
        all_items: list[ContextSourceFragment] = []

        def include(source_type: str) -> bool:
            return not requested or source_type in requested

        snapshot = ProjectIntelligenceService(self.db).get_or_refresh(project, refresh=False)
        retrieval = ProjectContextRetrievalService(self.db).retrieve(
            project,
            task_text=task_text,
            opened_file_path=opened_file_path,
            opened_file_content=opened_file_content,
            max_files=max(6, max_items_per_source),
            max_fragments=max(6, max_items_per_source),
            max_memory=max(6, max_items_per_source),
            max_history=max(6, max_items_per_source),
        )

        if include('project_metadata'):
            content = f'name={project.name}; platform={project.platform}; board={project.board}; branch={project.current_branch}; version={project.current_version}'
            all_items.append(self._fragment(project.id, 'project_metadata', content, 'stable', 100, summary=True))

        if include('project_intelligence_summary'):
            all_items.append(self._fragment(project.id, 'project_intelligence_summary', snapshot.summary, 'recent', 95, summary=True))

        if include('important_files'):
            content = '\n'.join(snapshot.important_files[: max_items_per_source * 2])
            all_items.append(self._fragment(project.id, 'important_files', content, 'recent', 92, summary=False))

        if include('open_selected_file') and opened_file_path:
            content = f'path={opened_file_path}\n{(opened_file_content or "")[:3000]}'
            all_items.append(self._fragment(project.id, 'open_selected_file', content, 'live', 98, summary=False))

        if include('retrieval_top_files'):
            top = retrieval.files[:max_items_per_source]
            content = '\n'.join([f"{it.path} score={it.score.total} reasons={','.join(it.score.reasons[:4])}" for it in top])
            all_items.append(self._fragment(project.id, 'retrieval_top_files', content, 'live', 99, summary=True))

        if include('retrieval_top_fragments'):
            top = retrieval.fragments[:max_items_per_source]
            content = '\n\n'.join([f"file={it.path} score={it.score.total}\n{it.snippet[:800]}" for it in top])
            all_items.append(self._fragment(project.id, 'retrieval_top_fragments', content, 'live', 99, summary=False))

        if include('retrieval_top_memory'):
            top = retrieval.memory[:max_items_per_source]
            content = '\n'.join([f"[{it.memory_type}] {it.title} score={it.score.total}: {it.content[:200]}" for it in top])
            all_items.append(self._fragment(project.id, 'retrieval_top_memory', content, 'recent', 97, summary=True))

        if include('retrieval_top_history'):
            top = retrieval.history[:max_items_per_source]
            content = '\n'.join([f"[{it.item_type}] {it.title} score={it.score.total}: {it.content[:220]}" for it in top])
            all_items.append(self._fragment(project.id, 'retrieval_top_history', content, 'recent', 89, summary=True))

        if include('recent_changed_files'):
            changed = self._recent_changed_files(project.path, max_items_per_source * 3)
            all_items.append(self._fragment(project.id, 'recent_changed_files', '\n'.join(changed), 'live', 90, summary=False))

        if include('git_diff_status'):
            content = self._git_diff_status(project.path)
            all_items.append(self._fragment(project.id, 'git_diff_status', content[:6000], 'live', 88, summary=True))

        if include('recent_commits'):
            commits = self._recent_commits(project.path, max_items_per_source)
            all_items.append(self._fragment(project.id, 'recent_commits', '\n'.join(commits), 'recent', 82, summary=True))

        if include('build_summary'):
            jobs = BuildService(self.db).list_jobs(project.id)
            summary = jobs[0].error_summary if jobs else 'no build jobs'
            freshness = 'live' if jobs and jobs[0].status == 'running' else 'recent'
            all_items.append(self._fragment(project.id, 'build_summary', summary, freshness, 91, summary=True))

        if include('important_build_logs'):
            content = self._important_build_logs(project.id)
            all_items.append(self._fragment(project.id, 'important_build_logs', content, 'recent', 93, summary=True))

        if include('important_runtime_logs'):
            content = self._important_runtime_logs(project.id)
            all_items.append(self._fragment(project.id, 'important_runtime_logs', content, 'recent', 93, summary=True))

        if include('project_memory'):
            content = AIMemoryService(self.db).summary(project.id)
            all_items.append(self._fragment(project.id, 'project_memory', content, 'recent', 96, summary=True))

        if include('prompt_memory'):
            current_prompt = PromptService(self.db).get_current_prompt(project.id)
            versions = PromptVersionService(self.db).list_versions(project.id)[:max_items_per_source]
            versions_text = '\n'.join([f"{row.version}: {row.prompt_text[:180]}" for row in versions])
            all_items.append(self._fragment(project.id, 'prompt_memory', f'current:\n{current_prompt[:800]}\nversions:\n{versions_text}', 'stable', 75, summary=True))

        if include('recent_agent_tasks'):
            tasks = AITaskService(self.db).list(project.id)[:max_items_per_source]
            content = '\n'.join([f"#{t.id} {t.task_type} status={t.status} output={t.output_text[:200]}" for t in tasks])
            all_items.append(self._fragment(project.id, 'recent_agent_tasks', content, 'recent', 87, summary=True))

        if include('dependency_toolchain_status'):
            deps = DependencyCheckService().check()
            toolchains = ToolchainDetectionService().detect()
            content = f'dependencies={deps}\ntoolchains={toolchains}'
            all_items.append(self._fragment(project.id, 'dependency_toolchain_status', content, 'stable', 70, summary=True))

        return all_items

    def _fragment(self, project_id: int, source_type: str, content: str, freshness: str, priority: int, summary: bool) -> ContextSourceFragment:
        text = content or ''
        meta = ContextSourceMeta(
            source_type=source_type,
            project_scope=project_id,
            freshness=freshness,
            estimated_size=len(text),
            priority=priority,
            retrievable=True,
            summary_available=summary,
        )
        return ContextSourceFragment(source_type=source_type, content=text, metadata=meta)

    @staticmethod
    def _recent_changed_files(repo_path: str, limit: int) -> list[str]:
        try:
            status = GitService().run(repo_path, ['status', '--short'])
        except Exception:
            return []
        lines = [line.strip() for line in status.splitlines() if line.strip()]
        files = [line[3:].strip() for line in lines if len(line) > 3]
        return files[:limit]

    @staticmethod
    def _git_diff_status(repo_path: str) -> str:
        try:
            status = GitService().run(repo_path, ['status', '--short'])
        except Exception:
            status = 'status unavailable'
        try:
            diff = GitDiffService().diff(repo_path)
        except Exception:
            diff = 'diff unavailable'
        return f'status:\n{status}\n\ndiff:\n{diff}'

    @staticmethod
    def _recent_commits(repo_path: str, limit: int) -> list[str]:
        try:
            output = GitService().run(repo_path, ['log', '--oneline', f'-n{max(1, limit)}'])
            return [line.strip() for line in output.splitlines() if line.strip()]
        except Exception:
            return []

    def _important_build_logs(self, project_id: int) -> str:
        jobs = BuildService(self.db).list_jobs(project_id)
        if not jobs:
            return 'no build jobs'
        latest = jobs[0]
        try:
            raw = Path(latest.log_path).read_text(encoding='utf-8')
        except Exception:
            raw = latest.error_summary or ''
        events = ImportantLogService().extract_events(raw, limit=160)
        compressed = LogSummaryService().compress(raw, events)
        return str(compressed.get('compressed_ai_context', ''))

    def _important_runtime_logs(self, project_id: int) -> str:
        session = (
            self.db.query(MonitorSession)
            .filter(MonitorSession.project_id == project_id)
            .order_by(MonitorSession.created_at.desc())
            .first()
        )
        if not session:
            return 'no runtime sessions'
        raw = SerialMonitorService(self.db).collect_runtime_log(session)
        events = ImportantLogService().extract_events(raw, limit=160)
        runtime = [e for e in events if e.get('stage') == 'runtime']
        if not runtime:
            return 'no important runtime logs'
        compressed = LogSummaryService().compress(raw, runtime)
        return str(compressed.get('compressed_ai_context', ''))
