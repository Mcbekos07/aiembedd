"""Git branches endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.git_branch import GitBranch
from app.db.session import get_db_session
from app.services.git.git_branch_service import GitBranchService
from app.services.history.event_write_service import EventWriteService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/branches', tags=['branches'])


class SwitchBranchRequest(BaseModel):
    branch_name: str


@router.get('/{project_id}')
def list_branches(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[str] | str]:
    project = ProjectService(db).get_project_by_id(project_id)
    service = GitBranchService()
    branches = service.list_branches(project.path)
    current = service.current_branch(project.path)

    db.query(GitBranch).filter(GitBranch.project_id == project_id).delete()
    for name in branches:
        db.add(GitBranch(project_id=project_id, name=name, is_active=name == current))
    db.commit()

    return {'status': 'ok', 'current_branch': current, 'branches': branches}


@router.post('/{project_id}/switch')
def switch_branch(project_id: int, payload: SwitchBranchRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    try:
        output = GitBranchService().switch_branch(project.path, payload.branch_name)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    project.current_branch = payload.branch_name
    db.commit()
    EventWriteService(db).write(project_id, 'branch_switched', 'Переключена ветка', payload.branch_name)
    return {'status': 'ok', 'message': 'Ветка переключена', 'output': output}
