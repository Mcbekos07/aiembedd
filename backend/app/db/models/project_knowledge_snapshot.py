"""Persisted project intelligence snapshot for agent context."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProjectKnowledgeSnapshot(Base):
    __tablename__ = 'project_knowledge_snapshots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, default='')
    architectural_notes: Mapped[str] = mapped_column(Text, default='')
    important_files: Mapped[list[str]] = mapped_column(JSON, default=list)
    risky_files: Mapped[list[str]] = mapped_column(JSON, default=list)
    known_build_paths: Mapped[list[str]] = mapped_column(JSON, default=list)
    entry_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    dependency_map: Mapped[dict[str, list[str]]] = mapped_column(JSON, default=dict)
    file_classification: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
