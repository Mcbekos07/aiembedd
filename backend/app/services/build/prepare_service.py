from pathlib import Path


class PrepareService:
    def prepare(self, repo_path: str, workspace_path: str) -> str:
        repo = Path(repo_path)
        workspace = Path(workspace_path)
        workspace.mkdir(parents=True, exist_ok=True)
        return f'Prepared workspace {workspace} from {repo}'
