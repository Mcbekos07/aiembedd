from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class CustomAdapter(ToolchainAdapter):
    name = 'custom'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via custom adapter']
