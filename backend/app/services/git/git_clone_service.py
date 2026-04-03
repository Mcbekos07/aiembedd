"""Git clone service."""

import subprocess
from pathlib import Path


class GitCloneService:
    def clone(self, remote_url: str, destination_path: str) -> str:
        Path(destination_path).resolve().parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(['git', 'clone', remote_url, destination_path], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or 'Не удалось клонировать репозиторий')
        return result.stdout.strip()
