from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AITaskAction(Base):
    __tablename__ = 'ai_task_actions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('ai_tasks.id', ondelete='CASCADE'), index=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    requires_confirmation: Mapped[str] = mapped_column(String(8), default='yes')
    payload: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
