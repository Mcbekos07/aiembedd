"""Project versions endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.project.project_service import ProjectService
from app.services.versioning.version_history_service import VersionHistoryService
from app.services.versioning.version_service import VersionService

router = APIRouter(prefix='/versions', tags=['versions'])


class CreateVersionRequest(BaseModel):
    kind: str = 'patch'
    note: str = ''
    with_tag: bool = False


@router.get('/{project_id}')
def list_versions(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    rows = VersionHistoryService(db).list_versions(project_id)
    return {'status': 'ok', 'items': [{'version': row.version, 'kind': row.kind, 'tag_name': row.tag_name, 'note': row.note, 'created_at': row.created_at.isoformat()} for row in rows]}


@router.post('/{project_id}')
def create_version(project_id: int, payload: CreateVersionRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    try:
        row = VersionService(db).create_version(project, payload.kind, payload.note, payload.with_tag)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {'status': 'ok', 'message': 'Версия создана', 'version': row.version, 'tag_name': row.tag_name}
