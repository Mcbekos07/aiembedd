from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class Esp32Adapter(ToolchainAdapter):
    name = 'esp32'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via esp32 adapter']
