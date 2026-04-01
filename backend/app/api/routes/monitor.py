from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.monitor.serial_monitor_service import SerialMonitorService

router = APIRouter(prefix='/monitor', tags=['monitor'])


class MonitorStartRequest(BaseModel):
    port: str
    baudrate: str = '115200'


@router.post('/{project_id}/start')
def start_monitor(project_id: int, payload: MonitorStartRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    session = SerialMonitorService(db).start(project_id, payload.port, payload.baudrate)
    return {'status': 'ok', 'session_id': str(session.id), 'message': 'Монитор запущен'}


@router.post('/sessions/{session_id}/stop')
def stop_monitor(session_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    SerialMonitorService(db).stop(session_id)
    return {'status': 'ok', 'message': 'Монитор остановлен'}
