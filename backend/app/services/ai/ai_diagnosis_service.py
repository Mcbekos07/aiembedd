"""Structured diagnosis flow built on existing AI provider and context services."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.schemas.ai_diagnosis import DiagnosisResult
from app.services.ai.ai_context_service import AIContextService
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.ai.ai_router_service import AIRouterService
from app.services.build.build_service import BuildService
from app.services.history.event_write_service import EventWriteService
from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService
from app.services.project.project_intelligence_service import ProjectIntelligenceService


class AIDiagnosisService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def diagnose(
        self,
        project: Project,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        task_text: str = '',
        mode: str = 'deep_build_fix',
    ) -> DiagnosisResult:
        result, _ = self.diagnose_with_report(project, opened_file_path, opened_file_content, task_text, mode)
        return result

    def diagnose_with_report(
        self,
        project: Project,
        opened_file_path: str | None = None,
        opened_file_content: str | None = None,
        task_text: str = '',
        mode: str = 'deep_build_fix',
    ) -> tuple[DiagnosisResult, dict[str, object]]:
        pipeline = AIContextService(self.db).build_diagnosis_with_report(project, opened_file_path, opened_file_content, task_text, mode=mode)
        context = str(pipeline['prompt_text'])
        _ = AIRouterService().route(project.ai_provider, project.ai_model, f'Diagnose build/runtime issue:\n{context}')

        snapshot = ProjectIntelligenceService(self.db).get_or_refresh(project, refresh=False)
        jobs = BuildService(self.db).list_jobs(project.id)
        failed_jobs = [j for j in jobs if j.status == 'failed']

        events: list[dict[str, object]] = []
        if failed_jobs:
            latest = failed_jobs[0]
            try:
                raw = Path(latest.log_path).read_text(encoding='utf-8')
            except Exception:
                raw = ''
            events = ImportantLogService().extract_events(raw)

        compressed = LogSummaryService().compress(raw if failed_jobs else '', events)
        summary_obj = compressed.get('root_cause_summary', {})
        memory_hits = AIMemoryService(self.db).query_context(project.id, [
            'successful_fix',
            'repeated_failure_pattern',
            'dependency_toolchain_caveat',
            'important_runtime_note',
            'project_invariant',
        ], limit=8)

        critical = [e for e in events if str(e.get('severity')) == 'critical']

        impacted = [str(e.get('file')) for e in critical if e.get('file')]
        impacted.extend([str(x) for x in compressed.get('links', {}).get('impacted_files', [])])
        if opened_file_path:
            impacted.insert(0, opened_file_path)
        impacted = list(dict.fromkeys(impacted))[:8]
        if not impacted:
            impacted = snapshot.important_files[:5]

        probable_cause = str(summary_obj.get('root_cause') or 'Недостаточно данных в логах; проверьте изменения и конфигурацию сборки.')
        problem_summary = str(summary_obj.get('summary') or 'Критичные проблемы не обнаружены, требуется ручная диагностика.')

        confidence = 'high' if critical and any(e.get('file') for e in critical) else ('medium' if critical else 'low')
        safe_auto_fix_possible = confidence == 'high' and all('linker_error' != e.get('error_type') for e in critical)

        recommended = [
            'Проверить compressed AI log context и хвост лога перед падением.',
            'Сверить include/import зависимости и сигнатуры функций.',
            'Проверить build конфигурацию и путь к артефактам.',
        ]
        if memory_hits:
            recommended.insert(0, f"Учитывать проектную память ({len(memory_hits)} записей): {memory_hits[0]['title']}")
        if not failed_jobs:
            recommended = ['Нет failed build истории: запустите сборку и повторите диагностику.']

        AIMemoryService(self.db).add_typed(
            project.id,
            'repeated_failure_pattern',
            problem_summary[:80] or 'diagnosis_pattern',
            probable_cause[:300],
            importance=3,
            source='diagnosis',
        )

        EventWriteService(self.db).write(project.id, 'context_pipeline_diagnosis', 'Context pipeline assembled for diagnosis', str(pipeline['report'])[:1500])

        return (
            DiagnosisResult(
                problem_summary=str(problem_summary),
                probable_cause=str(probable_cause),
                impacted_files=impacted,
                confidence_level=confidence,
                recommended_fix_actions=recommended,
                safe_auto_fix_possible=safe_auto_fix_possible,
            ),
            pipeline['report'],
        )
