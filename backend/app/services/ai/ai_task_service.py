from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_task import AITask


class AITaskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, project_id: int, task_type: str, input_text: str) -> AITask:
        task = AITask(project_id=project_id, task_type=task_type, input_text=input_text, status='running')
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def finish(self, task: AITask, output_text: str) -> AITask:
        task.output_text = output_text
        task.status = 'done'
        self.db.commit()
        return task

    def list(self, project_id: int) -> list[AITask]:
        stmt = select(AITask).where(AITask.project_id == project_id).order_by(AITask.created_at.desc())
        return list(self.db.scalars(stmt).all())
