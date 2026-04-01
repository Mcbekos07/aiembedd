from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MonitorSession(Base):
    __tablename__ = 'monitor_sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    port: Mapped[str] = mapped_column(String(128), default='')
    baudrate: Mapped[str] = mapped_column(String(16), default='115200')
    status: Mapped[str] = mapped_column(String(32), default='idle')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
