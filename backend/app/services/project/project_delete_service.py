"""Project delete service with selectable strategies."""

import shutil
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.exceptions import ProjectNotFoundError
from app.db.models.git_branch import GitBranch
from app.db.models.git_commit import GitCommit
from app.db.models.project import Project
from app.db.models.project_history import ProjectHistory
from app.db.models.project_remote import ProjectRemote
from app.db.models.version import Version
from app.utils.path import resolve_project_path


class ProjectDeleteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def execute(self, project_id: int, mode: str, confirmed: bool) -> None:
        if not confirmed:
            raise ValueError('Удаление требует подтверждения')

        project = self.db.get(Project, project_id)
        if not project:
            raise ProjectNotFoundError(f'Project {project_id} not found')

        if mode in {'registry_with_history', 'full'}:
            self._delete_history(project_id)

        if mode == 'full':
            self._delete_project_files(project.path)

        self.db.delete(project)
        self.db.commit()

    def _delete_history(self, project_id: int) -> None:
        for model in (ProjectHistory, GitCommit, GitBranch, Version, ProjectRemote):
            self.db.execute(delete(model).where(model.project_id == project_id))

    @staticmethod
    def _delete_project_files(project_path: str) -> None:
        path = resolve_project_path(project_path)
        if str(path) in {'/', str(Path.home())}:
            raise ValueError('Удаление системного каталога запрещено')
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
