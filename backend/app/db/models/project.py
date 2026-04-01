"""Project registry ORM model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_AI_MODEL, DEFAULT_AI_PROVIDER, DEFAULT_BRANCH, DEFAULT_VERSION
from app.db.base import Base


class Project(Base):
    """Embedded project registry entity."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    platform: Mapped[str] = mapped_column(String(64), default="custom")
    chip: Mapped[str] = mapped_column(String(128), default="")
    board: Mapped[str] = mapped_column(String(128), default="")
    build_system: Mapped[str] = mapped_column(String(64), default="custom")
    toolchain: Mapped[str] = mapped_column(String(128), default="")
    current_branch: Mapped[str] = mapped_column(String(64), default=DEFAULT_BRANCH)
    current_version: Mapped[str] = mapped_column(String(32), default=DEFAULT_VERSION)
    default_programmer: Mapped[str] = mapped_column(String(128), default="")
    default_port: Mapped[str] = mapped_column(String(128), default="")
    ai_provider: Mapped[str] = mapped_column(String(64), default=DEFAULT_AI_PROVIDER)
    ai_model: Mapped[str] = mapped_column(String(128), default=DEFAULT_AI_MODEL)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
