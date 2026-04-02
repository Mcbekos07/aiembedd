import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_task import AITask
from app.db.models.ai_task_action import AITaskAction


class AITaskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, project_id: int, task_type: str, input_text: str) -> AITask:
        task = AITask(project_id=project_id, task_type=task_type, input_text=input_text, status='queued')
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def set_status(self, task: AITask, status: str) -> AITask:
        task.status = status
        self.db.commit()
        self.db.refresh(task)
        return task

    def finish(self, task: AITask, output_text: str) -> AITask:
        task.output_text = output_text
        task.status = 'succeeded'
        self.db.commit()
        return task

    def fail(self, task: AITask, output_text: str) -> AITask:
        task.output_text = output_text
        task.status = 'failed'
        self.db.commit()
        return task

    def add_action(self, task_id: int, action_type: str, payload: dict[str, object], requires_confirmation: bool = False) -> AITaskAction:
        row = AITaskAction(
            task_id=task_id,
            action_type=action_type,
            requires_confirmation='yes' if requires_confirmation else 'no',
            payload=json.dumps(payload, ensure_ascii=False),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_actions(self, task_id: int) -> list[AITaskAction]:
        stmt = select(AITaskAction).where(AITaskAction.task_id == task_id).order_by(AITaskAction.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def list(self, project_id: int) -> list[AITask]:
        stmt = select(AITask).where(AITask.project_id == project_id).order_by(AITask.created_at.desc())
        return list(self.db.scalars(stmt).all())
