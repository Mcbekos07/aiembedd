from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class Mcs51Adapter(ToolchainAdapter):
    name = 'mcs51'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via mcs51 adapter']
