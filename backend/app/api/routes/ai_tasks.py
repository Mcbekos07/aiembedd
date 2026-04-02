import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.ai_diagnosis import DiagnosisRequest, DiagnosisResult
from app.services.ai.ai_diagnosis_service import AIDiagnosisService
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
    return {
        'status': 'ok',
        'items': [
            {
                'id': str(r.id),
                'task_type': r.task_type,
                'status': r.status,
                'input_text': r.input_text,
                'output_text': r.output_text,
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ],
    }


@router.get('/{project_id}/{task_id}/actions')
def list_task_actions(project_id: int, task_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    _ = ProjectService(db).get_project_by_id(project_id)
    items = []
    for row in AITaskService(db).list_actions(task_id):
        try:
            payload = json.loads(row.payload or '{}')
        except Exception:
            payload = {'raw': row.payload}
        items.append(
            {
                'id': row.id,
                'task_id': row.task_id,
                'action_type': row.action_type,
                'requires_confirmation': row.requires_confirmation,
                'payload': payload,
                'created_at': row.created_at.isoformat(),
            }
        )
    return {'status': 'ok', 'items': items}


@router.post('/{project_id}')
def run_task(project_id: int, payload: TaskRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    result = AITaskRunner(db).run(project, payload.task_type, payload.input_text)
    return {'status': 'ok', 'result': result}


@router.post('/{project_id}/diagnose', response_model=DiagnosisResult)
def diagnose_project(project_id: int, payload: DiagnosisRequest, db: Session = Depends(get_db_session)) -> DiagnosisResult:
    project = ProjectService(db).get_project_by_id(project_id)
    return AIDiagnosisService(db).diagnose(project, payload.opened_file_path, payload.opened_file_content, payload.task_text, payload.mode)
