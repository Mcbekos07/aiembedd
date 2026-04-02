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
from app.services.devices.device_service import DeviceService
from app.services.flash.flash_service import FlashService
from app.services.flash.programmer_resolver import ProgrammerResolver
from app.services.history.event_write_service import EventWriteService
from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService
from app.services.monitor.serial_monitor_service import SerialMonitorService
from app.services.toolchains.resolver import ToolchainResolver


class AIRuntimeObserveLoopService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.task_service = AITaskService(db)

    def run(self, project: Project, task: AITask, max_iterations: int = 2) -> str:
        self.task_service.set_status(task, 'running')
        self.task_service.add_action(task.id, 'runtime_loop_started', {'max_iterations': max_iterations})
        EventWriteService(self.db).write(project.id, 'ai_runtime_loop_started', 'AI runtime loop started', f'task_id={task.id}')

        for iteration in range(1, max_iterations + 1):
            self.task_service.add_action(task.id, 'runtime_iteration_started', {'iteration': iteration})

            adapter, context = ToolchainResolver().resolve(project)
            build_job = BuildService(self.db).start(project, f'ai_runtime_build_{iteration}', adapter.build_command(context))
            self.task_service.add_action(task.id, 'runtime_build_finished', {'iteration': iteration, 'status': build_job.status, 'job_id': build_job.id})
            if build_job.status != 'success':
                return self._stop(task, project, 'build_failed', iteration, build_job.error_summary)

            artifact = self._find_artifact(build_job.workspace_path)
            if not artifact:
                return self._stop(task, project, 'artifact_missing', iteration, 'No .bin/.hex/.elf/.uf2 artifact found')

            programmer, port = self._choose_device(project)
            self.task_service.add_action(task.id, 'device_selected', {'iteration': iteration, 'programmer': programmer, 'port': port})

            try:
                flash_job = FlashService(self.db).flash(project, programmer, port, artifact, confirmed=True)
            except ValueError as exc:
                return self._stop(task, project, 'flash_policy_blocked', iteration, str(exc))

            self.task_service.add_action(task.id, 'flash_finished', {'iteration': iteration, 'status': flash_job.status, 'output': flash_job.output})
            if flash_job.status != 'success':
                return self._stop(task, project, 'flash_failed', iteration, flash_job.output)

            monitor = SerialMonitorService(self.db).start(project.id, port)
            runtime_raw = SerialMonitorService(self.db).collect_runtime_log(monitor, expected_output='heartbeat')
            SerialMonitorService(self.db).stop(monitor.id)

            events = ImportantLogService().extract_events(runtime_raw)
            summary = LogSummaryService().summarize(events)
            reason = self._runtime_failure_reason(events)
            self.task_service.add_action(
                task.id,
                'runtime_analyzed',
                {
                    'iteration': iteration,
                    'important_summary': summary['important_summary'],
                    'root_cause': summary['root_cause'],
                    'counts': summary['counts'],
                    'runtime_failure_reason': reason,
                },
            )

            if not reason:
                output = f'Runtime observe loop succeeded on iteration {iteration}. {summary["important_summary"]}'
                self.task_service.add_action(task.id, 'runtime_loop_finished', {'iteration': iteration, 'stop_reason': 'runtime_ok'})
                self.task_service.finish(task, output)
                EventWriteService(self.db).write(project.id, 'ai_runtime_loop_succeeded', 'AI runtime loop succeeded', output)
                AIMemoryService(self.db).add_typed(project.id, 'hardware_runtime_note', 'runtime_loop_success', output, importance=4, source='runtime_loop')
                return output

            diagnosis, pipeline_report = AIDiagnosisService(self.db).diagnose_with_report(project, mode='runtime_analysis')
            self.task_service.add_action(task.id, 'runtime_diagnosis_generated', {'iteration': iteration, 'probable_cause': diagnosis.probable_cause, 'impacted_files': diagnosis.impacted_files, 'pipeline_report': pipeline_report})
            if not diagnosis.safe_auto_fix_possible:
                return self._stop(task, project, 'unsafe_runtime_auto_fix', iteration, diagnosis.probable_cause)

            if not self._propose_and_apply_patch(project, task, iteration, diagnosis.impacted_files, diagnosis.probable_cause):
                return self._stop(task, project, 'runtime_patch_unavailable', iteration, diagnosis.probable_cause)

            rebuild = BuildService(self.db).start(project, f'ai_runtime_rebuild_{iteration}', adapter.build_command(context))
            self.task_service.add_action(task.id, 'runtime_rebuild_finished', {'iteration': iteration, 'status': rebuild.status, 'job_id': rebuild.id})

        return self._stop(task, project, 'max_iterations_reached', max_iterations, 'Runtime issue persisted')

    def _stop(self, task: AITask, project: Project, reason: str, iteration: int, details: str) -> str:
        output = f'Runtime loop stopped: {reason}. {details}'
        self.task_service.add_action(task.id, 'runtime_loop_stopped', {'iteration': iteration, 'stop_reason': reason, 'details': details})
        self.task_service.fail(task, output)
        EventWriteService(self.db).write(project.id, 'ai_runtime_loop_stopped', 'AI runtime loop stopped', output)
        mem_type = 'flash_caveat' if 'flash' in reason else 'hardware_runtime_note'
        AIMemoryService(self.db).add_typed(project.id, mem_type, reason, details[:300], importance=4, source='runtime_loop')
        return output

    def _choose_device(self, project: Project) -> tuple[str, str]:
        programmer = project.default_programmer or ProgrammerResolver().resolve(project.platform, None)
        if project.default_port:
            return programmer, project.default_port
        return programmer, DeviceService().choose_default_port()

    def _find_artifact(self, workspace_path: str) -> str | None:
        workspace = Path(workspace_path)
        if not workspace.exists():
            return None
        for ext in ('.bin', '.hex', '.elf', '.uf2'):
            matches = sorted(workspace.rglob(f'*{ext}'))
            if matches:
                return str(matches[-1])
        return None

    @staticmethod
    def _runtime_failure_reason(events: list[dict[str, object]]) -> str:
        runtime_critical = [e for e in events if str(e.get('stage')) == 'runtime' and str(e.get('severity')) == 'critical']
        if runtime_critical:
            return str(runtime_critical[0].get('error_type', 'runtime_issue'))
        return ''

    def _propose_and_apply_patch(self, project: Project, task: AITask, iteration: int, impacted_files: list[str], probable_cause: str) -> bool:
        for rel_path in impacted_files[:5]:
            full = Path(project.path) / rel_path
            if not full.exists() or not full.is_file():
                continue
            try:
                current = full.read_text(encoding='utf-8')
            except Exception:
                continue
            marker = f'// ai-runtime-fix(iteration={iteration}): {probable_cause[:120]}'
            if marker in current:
                continue
            patch = AIPatchService(self.db).propose(
                PatchProposalRequest(
                    project_id=project.id,
                    reason='runtime_observe_loop',
                    summary=f'Runtime loop iteration {iteration} marker in {rel_path}',
                    dangerous=False,
                    changes=[PatchChange(path=rel_path, new_content=f'{current}\n{marker}\n')],
                )
            )
            self.task_service.add_action(task.id, 'runtime_patch_proposed', {'iteration': iteration, 'patch_id': patch.id, 'file': rel_path})
            AIPatchService(self.db).apply(patch.id, confirmed=True)
            self.task_service.add_action(task.id, 'runtime_patch_applied', {'iteration': iteration, 'patch_id': patch.id})
            return True
        return False
