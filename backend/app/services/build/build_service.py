from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.build_job import BuildJob
from app.db.models.project import Project
from app.services.build.artifact_collect_service import ArtifactCollectService
from app.services.build.build_executor_service import BuildExecutorService
from app.services.build.build_summary_service import BuildSummaryService
from app.services.build.build_workspace_service import BuildWorkspaceService
from app.services.build.prepare_service import PrepareService


class BuildService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def start(self, project: Project, action: str, command: list[str]) -> BuildJob:
        workspace = BuildWorkspaceService().create_workspace(project.id)
        log_path = workspace / 'build.log'
        PrepareService().prepare(project.path, str(workspace))

        job = BuildJob(project_id=project.id, action=action, status='running', workspace_path=str(workspace), log_path=str(log_path))
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        code, raw_log = BuildExecutorService().run(command, Path(project.path), log_path)
        job.status = 'success' if code == 0 else 'failed'
        job.error_summary = '\n'.join(BuildSummaryService().summarize(raw_log))
        self.db.commit()

        return job

    def stop(self, job: BuildJob) -> BuildJob:
        job.status = 'stopped'
        self.db.commit()
        return job

    def list_jobs(self, project_id: int) -> list[BuildJob]:
        return list(self.db.query(BuildJob).filter(BuildJob.project_id == project_id).order_by(BuildJob.created_at.desc()).all())

    def collect_artifacts(self, job: BuildJob) -> list[str]:
        artifacts = ArtifactCollectService().collect(Path(job.workspace_path))
        return [str(item) for item in artifacts]
