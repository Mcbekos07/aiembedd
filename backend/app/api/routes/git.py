"""Git orchestration endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.ai_task import AITask
from app.db.session import get_db_session
from app.services.git.git_checkpoint_service import GitCheckpointService
from app.services.git.git_commit_service import GitCommitService
from app.services.git.git_diff_service import GitDiffService
from app.services.git.git_init_service import GitInitService
from app.services.project.project_service import ProjectService
from app.services.versioning.version_service import VersionService

router = APIRouter(prefix='/git', tags=['git'])


class CommitRequest(BaseModel):
    message: str


class CheckpointCreateRequest(BaseModel):
    checkpoint_type: str = 'manual'
    message: str = 'Manual checkpoint'
    task_id: int = 0
    note: str = ''


class CheckpointRestoreRequest(BaseModel):
    checkpoint_id: int


class SuggestMessageRequest(BaseModel):
    task_id: int


class VersionFromTaskRequest(BaseModel):
    task_id: int
    kind: str = 'patch'
    note: str = ''
    with_tag: bool = False


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


@router.get('/{project_id}/checkpoints')
def list_checkpoints(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    _ = ProjectService(db).get_project_by_id(project_id)
    rows = GitCheckpointService(db).list_checkpoints(project_id)
    return {
        'status': 'ok',
        'items': [
            {
                'id': row.id,
                'task_id': row.task_id,
                'checkpoint_type': row.checkpoint_type,
                'git_ref': row.git_ref,
                'commit_message': row.commit_message,
                'status': row.status,
                'note': row.note,
                'created_at': row.created_at.isoformat(),
            }
            for row in rows
        ],
    }


@router.post('/{project_id}/checkpoints')
def create_checkpoint(project_id: int, payload: CheckpointCreateRequest, db: Session = Depends(get_db_session)) -> dict[str, object]:
    project = ProjectService(db).get_project_by_id(project_id)
    try:
        row = GitCheckpointService(db).create_checkpoint(
            project,
            payload.checkpoint_type,
            payload.message,
            task_id=payload.task_id,
            note=payload.note,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {'status': 'ok', 'checkpoint_id': row.id, 'git_ref': row.git_ref}


@router.post('/{project_id}/checkpoints/restore')
def restore_checkpoint(project_id: int, payload: CheckpointRestoreRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    try:
        row = GitCheckpointService(db).restore_checkpoint(project, payload.checkpoint_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {'status': 'ok', 'message': 'Checkpoint restored', 'git_ref': row.git_ref}


@router.post('/{project_id}/suggest-commit-message')
def suggest_commit_message(project_id: int, payload: SuggestMessageRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    _ = ProjectService(db).get_project_by_id(project_id)
    task = db.get(AITask, payload.task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=404, detail='Task not found')
    message = GitCheckpointService(db).suggest_commit_message(task.task_type, task.output_text)
    return {'status': 'ok', 'message': message}


@router.post('/{project_id}/version-from-task')
def version_from_task(project_id: int, payload: VersionFromTaskRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    task = db.get(AITask, payload.task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=404, detail='Task not found')

    try:
        note = payload.note or f'Agent task {task.task_type} ({task.status})'
        row = VersionService(db).create_version(project, payload.kind, note=note, with_tag=payload.with_tag)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {'status': 'ok', 'version': row.version, 'tag_name': row.tag_name}
