from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.build_job import BuildJob
from app.db.session import get_db_session
from app.services.build.build_service import BuildService
from app.services.project.project_service import ProjectService
from app.services.toolchains.resolver import ToolchainResolver

router = APIRouter(prefix='/builds', tags=['builds'])


class BuildActionRequest(BaseModel):
    action: str = 'build'


@router.post('/{project_id}/prepare')
def prepare(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    adapter, context = ToolchainResolver().resolve(project)
    job = BuildService(db).start(project, 'prepare', adapter.prepare_command(context))
    return {'status': job.status, 'job_id': str(job.id), 'message': 'Подготовка выполнена'}


@router.post('/{project_id}/run')
def build(project_id: int, payload: BuildActionRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    adapter, context = ToolchainResolver().resolve(project)
    command = adapter.build_command(context)
    job = BuildService(db).start(project, payload.action, command)
    return {'status': job.status, 'job_id': str(job.id), 'error_summary': job.error_summary}


@router.post('/{project_id}/clean')
def clean(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    job = BuildService(db).start(project, 'clean', ['echo', 'clean done'])
    return {'status': job.status, 'job_id': str(job.id), 'message': 'Очистка завершена'}


@router.post('/{project_id}/rebuild')
def rebuild(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    job = BuildService(db).start(project, 'rebuild', ['echo', 'rebuild done'])
    return {'status': job.status, 'job_id': str(job.id), 'message': 'Пересборка завершена'}


@router.post('/jobs/{job_id}/stop')
def stop(job_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    job = db.get(BuildJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Build job не найден')
    BuildService(db).stop(job)
    return {'status': 'ok', 'message': 'Job остановлен'}


@router.get('/{project_id}/history')
def history(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    jobs = BuildService(db).list_jobs(project_id)
    return {'status': 'ok', 'items': [{'id': str(item.id), 'action': item.action, 'status': item.status, 'created_at': item.created_at.isoformat()} for item in jobs]}
