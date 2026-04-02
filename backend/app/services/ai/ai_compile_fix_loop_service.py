from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.ai_task import AITask
from app.db.models.project import Project
from app.schemas.ai_patch import PatchChange, PatchProposalRequest
from app.services.ai.ai_diagnosis_service import AIDiagnosisService
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.ai.ai_patch_service import AIPatchService
from app.services.ai.ai_task_service import AITaskService
from app.services.build.build_service import BuildService
from app.services.history.event_write_service import EventWriteService
from app.services.toolchains.resolver import ToolchainResolver


class AICompileFixLoopService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.task_service = AITaskService(db)

    def run(self, project: Project, task: AITask, max_iterations: int = 3) -> str:
        self.task_service.set_status(task, 'running')
        self.task_service.add_action(task.id, 'loop_started', {'max_iterations': max_iterations})
        EventWriteService(self.db).write(project.id, 'ai_task_loop_started', 'AI compile-fix loop started', f'task_id={task.id}')

        for iteration in range(1, max_iterations + 1):
            self.task_service.add_action(task.id, 'iteration_started', {'iteration': iteration})

            adapter, context = ToolchainResolver().resolve(project)
            job = BuildService(self.db).start(project, f'ai_auto_fix_build_{iteration}', adapter.build_command(context))
            self.task_service.add_action(
                task.id,
                'build_finished',
                {
                    'iteration': iteration,
                    'job_id': job.id,
                    'build_status': job.status,
                    'error_summary': job.error_summary,
                },
            )

            if job.status == 'success':
                stop_reason = 'build_succeeded'
                output = f'Loop finished: build succeeded on iteration {iteration}.'
                self.task_service.add_action(task.id, 'loop_finished', {'stop_reason': stop_reason, 'iteration': iteration})
                self.task_service.finish(task, output)
                EventWriteService(self.db).write(project.id, 'ai_task_loop_succeeded', 'AI compile-fix loop succeeded', output)
                AIMemoryService(self.db).add_typed(project.id, 'known_good_fix', 'compile_loop_success', output, importance=4, source='build_loop')
                return output

            diagnosis, pipeline_report = AIDiagnosisService(self.db).diagnose_with_report(project, mode='deep_build_fix')
            self.task_service.add_action(
                task.id,
                'diagnosis_generated',
                {
                    'iteration': iteration,
                    'problem_summary': diagnosis.problem_summary,
                    'probable_cause': diagnosis.probable_cause,
                    'confidence_level': diagnosis.confidence_level,
                    'safe_auto_fix_possible': diagnosis.safe_auto_fix_possible,
                    'impacted_files': diagnosis.impacted_files,
                    'pipeline_report': pipeline_report,
                },
            )

            if not diagnosis.safe_auto_fix_possible:
                stop_reason = 'unsafe_auto_fix'
                output = f'Loop stopped: {stop_reason}. {diagnosis.probable_cause}'
                self.task_service.add_action(task.id, 'loop_stopped', {'stop_reason': stop_reason, 'iteration': iteration})
                self.task_service.fail(task, output)
                EventWriteService(self.db).write(project.id, 'ai_task_loop_stopped', 'AI compile-fix loop stopped', output)
                AIMemoryService(self.db).add_typed(project.id, 'build_caveat', stop_reason, output, importance=4, source='build_loop')
                return output

            patch_id = self._propose_and_apply_comment_patch(project, task, iteration, diagnosis.impacted_files, diagnosis.probable_cause)
            if not patch_id:
                stop_reason = 'no_safe_patch'
                output = 'Loop stopped: no safe patch could be generated from diagnosis.'
                self.task_service.add_action(task.id, 'loop_stopped', {'stop_reason': stop_reason, 'iteration': iteration})
                self.task_service.fail(task, output)
                EventWriteService(self.db).write(project.id, 'ai_task_loop_stopped', 'AI compile-fix loop stopped', output)
                AIMemoryService(self.db).add_typed(project.id, 'build_caveat', stop_reason, output, importance=3, source='build_loop')
                return output

        stop_reason = 'max_iterations_reached'
        output = f'Loop stopped: {stop_reason}.'
        self.task_service.add_action(task.id, 'loop_stopped', {'stop_reason': stop_reason, 'iteration': max_iterations})
        self.task_service.fail(task, output)
        EventWriteService(self.db).write(project.id, 'ai_task_loop_stopped', 'AI compile-fix loop stopped', output)
        AIMemoryService(self.db).add_typed(project.id, 'repeated_failure_pattern', stop_reason, output, importance=4, source='build_loop')
        return output

    def _propose_and_apply_comment_patch(
        self,
        project: Project,
        task: AITask,
        iteration: int,
        impacted_files: list[str],
        probable_cause: str,
    ) -> int | None:
        for rel_path in impacted_files[:5]:
            full_path = Path(project.path) / rel_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                current = full_path.read_text(encoding='utf-8')
            except Exception:
                continue

            comment_prefix = self._comment_prefix(full_path.suffix.lower())
            if not comment_prefix:
                continue

            marker = f'{comment_prefix} ai-auto-fix(iteration={iteration}): {probable_cause[:120]}'
            if marker in current:
                continue

            new_content = f'{current}\n{marker}\n'
            request = PatchProposalRequest(
                project_id=project.id,
                reason='compile_fix_loop',
                summary=f'Iteration {iteration} auto-fix marker in {rel_path}',
                dangerous=False,
                changes=[PatchChange(path=rel_path, new_content=new_content)],
            )

            patch = AIPatchService(self.db).propose(request)
            self.task_service.add_action(task.id, 'patch_proposed', {'iteration': iteration, 'patch_id': patch.id, 'files': [rel_path]})
            applied = AIPatchService(self.db).apply(patch.id, confirmed=True)
            self.task_service.add_action(task.id, 'patch_applied', {'iteration': iteration, 'patch_id': applied.id, 'git_status': applied.git_status_after_apply})
            return patch.id

        return None

    @staticmethod
    def _comment_prefix(suffix: str) -> str:
        if suffix in {'.py', '.sh', '.yml', '.yaml', '.toml', '.ini'}:
            return '#'
        if suffix in {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.js', '.ts', '.vue'}:
            return '//'
        return ''
