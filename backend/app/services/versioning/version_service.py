"""Project versioning service."""

from sqlalchemy.orm import Session

from app.db.models.project import Project
from app.db.models.version import Version
from app.services.git.git_tag_service import GitTagService
from app.services.history.event_write_service import EventWriteService
from app.services.versioning.semver_service import SemverService


class VersionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.semver = SemverService()
        self.tag_service = GitTagService()

    def create_version(self, project: Project, kind: str, note: str = '', with_tag: bool = False) -> Version:
        new_version = self.semver.bump(project.current_version, kind)
        tag_name = f'v{new_version}' if with_tag else ''

        version = Version(project_id=project.id, version=new_version, kind=kind, note=note, tag_name=tag_name)
        self.db.add(version)
        project.current_version = new_version
        self.db.commit()
        self.db.refresh(version)

        if with_tag:
            self.tag_service.create_tag(project.path, tag_name)

        EventWriteService(self.db).write(project.id, 'version_created', 'Создана версия', f'{new_version} ({kind})')
        return version
