"""Checks tool dependencies required by supported build/flash workflows."""

import shutil

from app.services.dependencies.constants import CHECKABLE_BINARIES


class DependencyCheckService:
    def check(self) -> list[dict[str, str]]:
        result = []
        for dep in CHECKABLE_BINARIES:
            path = shutil.which(dep) or ''
            result.append({'name': dep, 'status': 'found' if path else 'missing', 'path': path})
        return result
