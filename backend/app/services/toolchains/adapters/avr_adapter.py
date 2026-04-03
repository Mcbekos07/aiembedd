from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class AvrAdapter(ToolchainAdapter):
    name = 'avr'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via avr adapter']
