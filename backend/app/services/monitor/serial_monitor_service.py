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
