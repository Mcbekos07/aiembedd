"""Remote git endpoints (clone, fetch, pull, remotes)."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.paths import WORKSPACES_DIR
from app.db.models.project_remote import ProjectRemote
from app.db.session import get_db_session
from app.schemas.project import ProjectImportRequest
from app.services.git.git_clone_service import GitCloneService
from app.services.git.git_fetch_service import GitFetchService
from app.services.git.git_pull_service import GitPullService
from app.services.git.git_remote_service import GitRemoteService
from app.services.git.remote_policy_service import RemoteGitPolicyService
from app.services.history.event_write_service import EventWriteService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/remote-git', tags=['remote-git'])


class CloneRequest(BaseModel):
    remote_url: str
    project_name: str


class RemoteRequest(BaseModel):
    name: str
    url: str


def _safe_destination(project_name: str) -> Path:
    candidate = project_name.strip()
    if not candidate or '/' in candidate or '..' in candidate:
        raise ValueError('Некорректное имя проекта для clone')
    return Path(WORKSPACES_DIR) / candidate


@router.post('/clone')
def clone_remote(payload: CloneRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    policy = RemoteGitPolicyService()
    try:
        destination = _safe_destination(payload.project_name)
        policy.validate_remote_url(payload.remote_url)
        output = GitCloneService().clone(payload.remote_url, str(destination))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    created = ProjectService(db).import_local_project(
        ProjectImportRequest(
            name=payload.project_name,
            local_path=str(destination),
            description='Клонирован из remote Git',
            platform='custom',
        )
    )
    EventWriteService(db).write(created.id, 'clone', 'Клонирование завершено', payload.remote_url)
    return {'status': 'ok', 'message': 'Проект клонирован', 'output': output}


@router.post('/{project_id}/fetch')
def fetch_remote(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    output = GitFetchService().fetch(project.path)
    EventWriteService(db).write(project_id, 'fetch', 'Выполнен fetch', '')
    return {'status': 'ok', 'message': 'Fetch выполнен', 'output': output}


@router.post('/{project_id}/pull')
def pull_remote(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    output = GitPullService().pull(project.path, branch=project.current_branch)
    EventWriteService(db).write(project_id, 'pull', 'Выполнен pull', project.current_branch)
    return {'status': 'ok', 'message': 'Pull выполнен', 'output': output}


@router.get('/{project_id}/remotes')
def list_remotes(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    output = GitRemoteService().list_remotes(project.path)
    return {'status': 'ok', 'output': output}


@router.post('/{project_id}/remotes')
def add_remote(project_id: int, payload: RemoteRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    policy = RemoteGitPolicyService()
    policy.validate_remote_name(payload.name)
    policy.validate_remote_url(payload.url)

    output = GitRemoteService().add_remote(project.path, payload.name, payload.url)
    db.add(ProjectRemote(project_id=project_id, name=payload.name, url=payload.url))
    db.commit()
    return {'status': 'ok', 'message': 'Remote добавлен', 'output': output}
