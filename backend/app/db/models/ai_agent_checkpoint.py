from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIAgentCheckpoint(Base):
    __tablename__ = 'ai_agent_checkpoints'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    task_id: Mapped[int] = mapped_column(Integer, default=0)
    checkpoint_type: Mapped[str] = mapped_column(String(64), default='manual')
    git_ref: Mapped[str] = mapped_column(String(64), default='')
    commit_message: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(32), default='created')
    note: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
