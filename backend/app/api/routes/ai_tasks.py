from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.ai.ai_task_runner import AITaskRunner
from app.services.ai.ai_task_service import AITaskService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/ai-tasks', tags=['ai-tasks'])


class TaskRequest(BaseModel):
    task_type: str
    input_text: str


@router.get('/{project_id}')
def list_tasks(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    rows = AITaskService(db).list(project_id)
    return {'status': 'ok', 'items': [{'id': str(r.id), 'task_type': r.task_type, 'status': r.status, 'created_at': r.created_at.isoformat()} for r in rows]}


@router.post('/{project_id}')
def run_task(project_id: int, payload: TaskRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    result = AITaskRunner(db).run(project, payload.task_type, payload.input_text)
    return {'status': 'ok', 'result': result}
