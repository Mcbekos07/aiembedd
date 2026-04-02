from app.services.toolchains.adapters.base import AdapterContext, ToolchainAdapter


class VerilogAdapter(ToolchainAdapter):
    name = 'verilog'

    def build_command(self, ctx: AdapterContext) -> list[str]:
        return ['echo', f'build for {ctx.platform} via verilog adapter']
