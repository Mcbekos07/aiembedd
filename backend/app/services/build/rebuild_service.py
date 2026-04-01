from app.services.build.clean_service import CleanService
from app.services.build.prepare_service import PrepareService


class RebuildService:
    def rebuild(self, repo_path: str, workspace_path: str) -> str:
        CleanService().clean(workspace_path)
        return PrepareService().prepare(repo_path, workspace_path)
