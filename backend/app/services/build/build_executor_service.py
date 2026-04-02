"""Build command executor with conservative command validation."""

import subprocess
from pathlib import Path

from app.services.build.log_capture_service import LogCaptureService


class BuildExecutorService:
    """Executes build command inside isolated workspace."""

    SAFE_BINARIES = {'echo', 'cmake', 'make', 'ninja', 'python3'}

    def run(self, command: list[str], cwd: Path, log_path: Path) -> tuple[int, str]:
        if not command:
            raise ValueError('Build command is empty')
        if command[0] not in self.SAFE_BINARIES:
            raise ValueError('Build command is blocked by policy')

        process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
        logger = LogCaptureService()
        stdout = process.stdout or ''
        stderr = process.stderr or ''
        if stdout:
            logger.append(log_path, stdout)
        if stderr:
            logger.append(log_path, stderr)
        return process.returncode, '\n'.join(part for part in (stdout, stderr) if part)
