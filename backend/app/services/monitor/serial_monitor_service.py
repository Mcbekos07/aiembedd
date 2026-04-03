from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.monitor_session import MonitorSession


class SerialMonitorService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def start(self, project_id: int, port: str, baudrate: str = '115200') -> MonitorSession:
        session = MonitorSession(project_id=project_id, port=port, baudrate=baudrate, status='running')
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def stop(self, session_id: int) -> MonitorSession | None:
        session = self.db.get(MonitorSession, session_id)
        if session:
            session.status = 'stopped'
            self.db.commit()
        return session

    def active_for_project(self, project_id: int) -> MonitorSession | None:
        return (
            self.db.query(MonitorSession)
            .filter(MonitorSession.project_id == project_id, MonitorSession.status == 'running')
            .order_by(MonitorSession.created_at.desc())
            .first()
        )

    def collect_runtime_log(self, session: MonitorSession, expected_output: str = '') -> str:
        # Stub runtime stream until real serial backend is connected.
        lines = [
            f'[serial] port={session.port} baud={session.baudrate}',
            'boot: application start',
            'init: peripherals ready',
            'runtime: heartbeat',
        ]
        if expected_output and expected_output.lower() not in ' '.join(lines).lower():
            lines.append(f'no expected output: {expected_output}')
        return '\n'.join(lines)
