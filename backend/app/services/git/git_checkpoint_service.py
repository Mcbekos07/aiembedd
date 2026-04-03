from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_agent_checkpoint import AIAgentCheckpoint
from app.db.models.project import Project
from app.services.git.git_service import GitService
from app.services.history.event_write_service import EventWriteService


class GitCheckpointService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.git = GitService()

    def create_checkpoint(
        self,
        project: Project,
        checkpoint_type: str,
        message: str,
        *,
        task_id: int = 0,
        note: str = '',
    ) -> AIAgentCheckpoint:
        commit_message = f'[agent-checkpoint:{checkpoint_type}] {message}'.strip()
        self.git.run(project.path, ['add', '.'])
        self.git.run(project.path, ['commit', '--allow-empty', '-m', commit_message])
        commit_hash = self.git.run(project.path, ['rev-parse', 'HEAD'])

        row = AIAgentCheckpoint(
            project_id=project.id,
            task_id=task_id,
            checkpoint_type=checkpoint_type,
            git_ref=commit_hash,
            commit_message=commit_message,
            status='created',
            note=note,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        EventWriteService(self.db).write(project.id, 'agent_checkpoint_created', 'Agent checkpoint created', f'{checkpoint_type} #{row.id}')
        return row

    def list_checkpoints(self, project_id: int) -> list[AIAgentCheckpoint]:
        stmt = select(AIAgentCheckpoint).where(AIAgentCheckpoint.project_id == project_id).order_by(AIAgentCheckpoint.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def restore_checkpoint(self, project: Project, checkpoint_id: int) -> AIAgentCheckpoint:
        row = self.db.get(AIAgentCheckpoint, checkpoint_id)
        if not row or row.project_id != project.id:
            raise ValueError('Checkpoint not found')
        self.git.run(project.path, ['reset', '--hard', row.git_ref])
        row.status = 'restored'
        self.db.commit()
        EventWriteService(self.db).write(project.id, 'agent_checkpoint_restored', 'Agent checkpoint restored', f'checkpoint #{row.id}')
        return row

    def suggest_commit_message(self, task_type: str, task_output: str) -> str:
        tail = (task_output or '').strip().splitlines()
        headline = tail[0][:90] if tail else 'agent fix applied'
        return f'{task_type}: {headline}'
