"""Project history timeline endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.ai_task import AITask
from app.db.models.build_job import BuildJob
from app.db.models.project_history import ProjectHistory
from app.db.models.version import Version
from app.db.session import get_db_session

router = APIRouter(prefix='/history', tags=['history'])


@router.get('/{project_id}')
def get_history(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    items: list[dict[str, str]] = []

    for event in db.query(ProjectHistory).filter(ProjectHistory.project_id == project_id).all():
        items.append({'source': 'project_event', 'title': event.title, 'details': event.details, 'created_at': event.created_at.isoformat()})

    for job in db.query(BuildJob).filter(BuildJob.project_id == project_id).all():
        items.append({'source': 'build_job', 'title': f'Build {job.action}', 'details': job.status, 'created_at': job.created_at.isoformat()})

    for version in db.query(Version).filter(Version.project_id == project_id).all():
        items.append({'source': 'version', 'title': 'Создана версия', 'details': version.version, 'created_at': version.created_at.isoformat()})

    for task in db.query(AITask).filter(AITask.project_id == project_id).all():
        items.append({'source': 'ai_task', 'title': f'AI task {task.task_type}', 'details': task.status, 'created_at': task.created_at.isoformat()})

    items.sort(key=lambda row: row['created_at'], reverse=True)
    return {'status': 'ok', 'items': items}
