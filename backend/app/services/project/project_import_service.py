"""Service for importing local projects."""

from sqlalchemy.orm import Session

from app.core.enums import ProjectSourceType
from app.db.models.project import Project
from app.schemas.project import ProjectImportRequest
from app.services.history.event_write_service import EventWriteService
from app.utils.path import resolve_project_path


class ProjectImportService:
    """Handles local project import into registry."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def import_local(self, payload: ProjectImportRequest) -> Project:
        project_path = resolve_project_path(payload.local_path)

        project = Project(
            name=payload.name,
            description=payload.description,
            path=str(project_path),
            source_type=ProjectSourceType.LOCAL_IMPORT.value,
            platform=payload.platform,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        EventWriteService(self.db).write(project.id, 'project_imported', 'Импортирован проект', str(project_path))
        return project
