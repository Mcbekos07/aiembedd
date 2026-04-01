"""Base safe Git execution service."""

import subprocess
from pathlib import Path


class GitService:
    ALLOWED = {'status', 'init', 'clone', 'pull', 'fetch', 'branch', 'checkout', 'commit', 'diff', 'tag', 'remote', 'restore', 'add', 'rev-parse'}

    def run(self, repo_path: str, args: list[str]) -> str:
        if not args or args[0] not in self.ALLOWED:
            raise ValueError('Git команда не разрешена')

        resolved = Path(repo_path).resolve()
        result = subprocess.run(
            ['git', *args],
            cwd=resolved,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or 'Git команда завершилась с ошибкой')
        return result.stdout.strip()
