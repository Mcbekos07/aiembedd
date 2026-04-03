from pathlib import Path


class ArtifactCollectService:
    def collect(self, workspace: Path) -> list[Path]:
        artifacts: list[Path] = []
        for suffix in ('.elf', '.hex', '.bin', '.uf2'):
            artifacts.extend(workspace.rglob(f'*{suffix}'))
        return artifacts
