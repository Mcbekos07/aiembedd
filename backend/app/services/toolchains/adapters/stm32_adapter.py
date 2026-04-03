from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class Stm32Adapter(ToolchainAdapter):
    name = 'stm32'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via stm32 adapter']
