from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.flash.flash_service import FlashService
from app.services.flash.port_binding_service import PortBindingService
from app.services.flash.programmer_resolver import ProgrammerResolver
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/flash', tags=['flash'])


class FlashRequest(BaseModel):
    programmer: str | None = None
    port: str = '/dev/ttyUSB0'


@router.post('/{project_id}')
def flash(project_id: int, payload: FlashRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    programmer = ProgrammerResolver().resolve(project.platform, payload.programmer)
    PortBindingService().bind(db, project, payload.port, programmer)
    job = FlashService(db).flash(project_id, programmer, payload.port)
    return {'status': job.status, 'message': job.output}
