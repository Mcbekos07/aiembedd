from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class MicropythonAdapter(ToolchainAdapter):
    name = 'micropython'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via micropython adapter']
