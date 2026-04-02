from sqlalchemy.orm import Session

from app.db.models.project import Project


class PortBindingService:
    def bind(self, db: Session, project: Project, port: str, programmer: str) -> None:
        project.default_port = port
        project.default_programmer = programmer
        db.commit()
