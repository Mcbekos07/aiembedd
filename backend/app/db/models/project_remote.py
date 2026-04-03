"""Git remotes linked to projects."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProjectRemote(Base):
    __tablename__ = 'project_remotes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    name: Mapped[str] = mapped_column(String(64), default='origin')
    url: Mapped[str] = mapped_column(String(512), nullable=False)
