from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.build.build_service import BuildService
from app.services.flash.flash_service import FlashService
from app.services.flash.port_binding_service import PortBindingService
from app.services.flash.programmer_resolver import ProgrammerResolver
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/flash', tags=['flash'])


class FlashRequest(BaseModel):
    programmer: str | None = None
    port: str = '/dev/ttyUSB0'
    artifact_path: str | None = None
    confirmed: bool = False
    allow_mismatch: bool = False


@router.post('/{project_id}')
def flash(project_id: int, payload: FlashRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    programmer = ProgrammerResolver().resolve(project.platform, payload.programmer)
    artifact_path = payload.artifact_path or _find_latest_artifact(project_id, db)
    if not artifact_path:
        raise HTTPException(status_code=400, detail='Artifact not found. Build project first or pass artifact_path.')

    try:
        job = FlashService(db).flash(
            project,
            programmer,
            payload.port,
            artifact_path,
            confirmed=payload.confirmed,
            allow_mismatch=payload.allow_mismatch,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if job.status == 'success':
        PortBindingService().bind(db, project, payload.port, programmer)
    return {'status': job.status, 'message': job.output}


def _find_latest_artifact(project_id: int, db: Session) -> str | None:
    jobs = BuildService(db).list_jobs(project_id)
    for job in jobs:
        workspace = Path(job.workspace_path)
        if not workspace.exists():
            continue
        for ext in ('.bin', '.hex', '.elf', '.uf2'):
            hits = sorted(workspace.rglob(f'*{ext}'))
            if hits:
                return str(hits[-1])
    return None
