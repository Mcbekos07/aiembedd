"""Stored AI patch proposal/checkpoint lifecycle."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIPatchSet(Base):
    __tablename__ = 'ai_patch_sets'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    status: Mapped[str] = mapped_column(String(32), default='pending')  # pending/applied/rejected/rolled_back
    reason: Mapped[str] = mapped_column(Text, default='')
    summary: Mapped[str] = mapped_column(Text, default='')
    dangerous: Mapped[str] = mapped_column(String(8), default='no')
    changes: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list)
    checkpoint: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    diff_preview: Mapped[str] = mapped_column(Text, default='')
    git_status_after_apply: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
