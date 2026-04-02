from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.services.ai.ai_chat_service import AIChatService
from app.services.ai.ai_compile_fix_loop_service import AICompileFixLoopService
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.ai.ai_runtime_observe_loop_service import AIRuntimeObserveLoopService
from app.services.ai.ai_task_service import AITaskService
from app.services.git.git_checkpoint_service import GitCheckpointService
from app.services.versioning.version_service import VersionService


class AITaskRunner:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run(self, project: Project, task_type: str, input_text: str) -> str:
        task_service = AITaskService(self.db)
        task = task_service.create(project.id, task_type, input_text)

        if task_type in {'compile_fix_loop', 'runtime_observe_loop'}:
            checkpoint = None
            try:
                checkpoint = GitCheckpointService(self.db).create_checkpoint(
                    project,
                    'pre_agent_checkpoint',
                    f'{task_type} start',
                    task_id=task.id,
                )
                task_service.add_action(task.id, 'pre_agent_checkpoint_created', {'checkpoint_id': checkpoint.id, 'git_ref': checkpoint.git_ref})
            except Exception as exc:
                task_service.add_action(task.id, 'pre_agent_checkpoint_failed', {'reason': str(exc)})

            if task_type == 'compile_fix_loop':
                result = AICompileFixLoopService(self.db).run(project, task)
                AIMemoryService(self.db).compact_old_data(project.id)
            else:
                result = AIRuntimeObserveLoopService(self.db).run(project, task)
                AIMemoryService(self.db).promote_history_events(project.id, limit=10)
                AIMemoryService(self.db).compact_old_data(project.id)

            task_service.add_action(task.id, 'agent_commit_message_suggestion', {'message': GitCheckpointService(self.db).suggest_commit_message(task_type, result)})

            if task.status == 'succeeded':
                try:
                    version = VersionService(self.db).create_version(project, 'patch', note=f'Agent success task_id={task.id}', with_tag=False)
                    task_service.add_action(task.id, 'successful_fix_snapshot', {'version': version.version, 'note': version.note})
                except Exception as exc:
                    task_service.add_action(task.id, 'successful_fix_snapshot_failed', {'reason': str(exc)})
            else:
                if checkpoint:
                    task_service.add_action(task.id, 'rollback_option', {'checkpoint_id': checkpoint.id, 'git_ref': checkpoint.git_ref})

            return result

        task_service.set_status(task, 'running')
        answer = AIChatService(self.db).send(project, f'[{task_type}] {input_text}').content
        task_service.finish(task, answer)
        return answer
