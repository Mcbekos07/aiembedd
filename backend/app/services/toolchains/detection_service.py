import shutil

from app.services.toolchains.registry import ToolchainRegistry


class ToolchainDetectionService:
    def detect(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for name in ToolchainRegistry().list_names():
            binary = 'gcc' if name != 'micropython' else 'python3'
            detected = shutil.which(binary) or ''
            result.append({'name': name, 'status': 'found' if detected else 'missing', 'path': detected})
        return result
