import shutil
from pathlib import Path


class CleanService:
    def clean(self, workspace_path: str) -> str:
        workspace = Path(workspace_path)
        if workspace.exists():
            shutil.rmtree(workspace)
        return f'Workspace cleaned: {workspace}'
