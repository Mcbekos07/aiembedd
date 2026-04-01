"""Project registry service facade."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError
from app.db.models.project import Project
from app.schemas.project import ProjectCreateRequest, ProjectImportRequest
from app.services.project.project_create_service import ProjectCreateService
from app.services.project.project_import_service import ProjectImportService


class ProjectService:
    """Provides CRUD-like operations for project registry."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.create_service = ProjectCreateService(db)
        self.import_service = ProjectImportService(db)

    def create_project(self, payload: ProjectCreateRequest) -> Project:
        return self.create_service.create(payload)

    def import_local_project(self, payload: ProjectImportRequest) -> Project:
        return self.import_service.import_local(payload)

    def get_project_list(self) -> list[Project]:
        return list(self.db.scalars(select(Project).order_by(Project.created_at.desc())).all())

    def get_project_by_id(self, project_id: int) -> Project:
        project = self.db.get(Project, project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        return project

    def delete_registry_only(self, project_id: int) -> None:
        project = self.get_project_by_id(project_id)
        self.db.delete(project)
        self.db.commit()
