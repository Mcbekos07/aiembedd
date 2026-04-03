"""Service for creating new projects."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.config.paths import WORKSPACES_DIR
from app.core.enums import ProjectSourceType
from app.db.models.project import Project
from app.schemas.project import ProjectCreateRequest
from app.services.history.event_write_service import EventWriteService


class ProjectCreateService:
    """Handles creation of project metadata and workspace path."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProjectCreateRequest) -> Project:
        project_dir = Path(WORKSPACES_DIR) / payload.name
        project_dir.mkdir(parents=True, exist_ok=True)

        project = Project(
            name=payload.name,
            description=payload.description,
            path=str(project_dir),
            source_type=ProjectSourceType.NEW.value,
            platform=payload.platform,
            chip=payload.chip,
            board=payload.board,
            build_system=payload.build_system,
            toolchain=payload.toolchain,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        EventWriteService(self.db).write(project.id, 'project_created', 'Создан проект', project.name)
        return project
