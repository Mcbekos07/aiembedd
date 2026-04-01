from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.services.ai.ai_chat_service import AIChatService
from app.services.ai.ai_task_service import AITaskService


class AITaskRunner:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run(self, project: Project, task_type: str, input_text: str) -> str:
        task_service = AITaskService(self.db)
        task = task_service.create(project.id, task_type, input_text)
        answer = AIChatService(self.db).send(project, f'[{task_type}] {input_text}').content
        task_service.finish(task, answer)
        return answer
