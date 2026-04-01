from app.db.models.project import Project
from app.services.toolchains.adapters.base import AdapterContext
from app.services.toolchains.registry import ToolchainRegistry


class ToolchainResolver:
    def resolve(self, project: Project):
        registry = ToolchainRegistry()
        adapter = registry.get(project.platform)
        context = AdapterContext(
            platform=project.platform,
            chip=project.chip,
            board=project.board,
            toolchain=project.toolchain,
        )
        return adapter, context
