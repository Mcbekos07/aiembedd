"""Git commit metadata model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GitCommit(Base):
    __tablename__ = 'git_commits'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(128), default='')
    branch_name: Mapped[str] = mapped_column(String(128), default='main')
    committed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
