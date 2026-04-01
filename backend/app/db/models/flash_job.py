from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FlashJob(Base):
    __tablename__ = 'flash_jobs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(32), default='queued')
    programmer: Mapped[str] = mapped_column(String(128), default='')
    port: Mapped[str] = mapped_column(String(128), default='')
    output: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
