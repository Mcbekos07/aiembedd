from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIProjectBinding(Base):
    __tablename__ = 'ai_project_bindings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    provider: Mapped[str] = mapped_column(String(64), default='openai')
    model: Mapped[str] = mapped_column(String(128), default='gpt-4.1-mini')
    permission_mode: Mapped[str] = mapped_column(String(64), default='suggest_only')
