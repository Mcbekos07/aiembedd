"""Git orchestration endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.git.git_commit_service import GitCommitService
from app.services.git.git_diff_service import GitDiffService
from app.services.git.git_init_service import GitInitService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/git', tags=['git'])


class CommitRequest(BaseModel):
    message: str


@router.post('/{project_id}/init')
def git_init(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    output = GitInitService().init_repo(project.path)
    return {'status': 'ok', 'message': 'Git инициализирован', 'output': output}


@router.get('/{project_id}/diff')
def git_diff(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    output = GitDiffService().diff(project.path)
    return {'status': 'ok', 'label': 'Diff', 'output': output}


@router.post('/{project_id}/commit')
def git_commit(project_id: int, payload: CommitRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    service = ProjectService(db)
    project = service.get_project_by_id(project_id)
    try:
        output = GitCommitService().commit_all(project.path, payload.message)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {'status': 'ok', 'message': 'Commit выполнен', 'output': output}
