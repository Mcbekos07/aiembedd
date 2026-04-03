from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.monitor_session import MonitorSession
from app.db.session import get_db_session
from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService
from app.services.monitor.serial_monitor_service import SerialMonitorService

router = APIRouter(prefix='/monitor', tags=['monitor'])


class MonitorStartRequest(BaseModel):
    port: str
    baudrate: str = '115200'


@router.post('/{project_id}/start')
def start_monitor(project_id: int, payload: MonitorStartRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    session = SerialMonitorService(db).start(project_id, payload.port, payload.baudrate)
    return {'status': 'ok', 'session_id': str(session.id), 'message': 'Монитор запущен'}


@router.get('/{project_id}/status')
def monitor_status(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    session = SerialMonitorService(db).active_for_project(project_id)
    if not session:
        return {'status': 'idle', 'session': None}
    return {
        'status': session.status,
        'session': {'id': session.id, 'port': session.port, 'baudrate': session.baudrate, 'created_at': session.created_at.isoformat()},
    }


@router.get('/sessions/{session_id}/logs')
def monitor_logs(session_id: int, expected_output: str = '', db: Session = Depends(get_db_session)) -> dict[str, object]:
    session = db.get(MonitorSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    raw_log = SerialMonitorService(db).collect_runtime_log(session, expected_output=expected_output)
    events = ImportantLogService().extract_events(raw_log)
    summary = LogSummaryService().summarize(events)

    return {
        'status': 'ok',
        'raw_log': raw_log,
        'important_events': events,
        'runtime_summary': summary['important_summary'],
        'root_cause': summary['root_cause'],
        'event_counts': summary['counts'],
    }


@router.post('/sessions/{session_id}/stop')
def stop_monitor(session_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    SerialMonitorService(db).stop(session_id)
    return {'status': 'ok', 'message': 'Монитор остановлен'}
