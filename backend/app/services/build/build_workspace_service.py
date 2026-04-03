from pathlib import Path
from uuid import uuid4

from app.config.paths import DATA_DIR


class BuildWorkspaceService:
    def create_workspace(self, project_id: int) -> Path:
        workspace = DATA_DIR / 'build_jobs' / f'project_{project_id}' / uuid4().hex
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
