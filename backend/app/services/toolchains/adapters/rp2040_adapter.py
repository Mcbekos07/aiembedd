from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class Rp2040Adapter(ToolchainAdapter):
    name = 'rp2040'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via rp2040 adapter']
