from dataclasses import dataclass


@dataclass
class AdapterContext:
    platform: str
    chip: str
    board: str
    toolchain: str


class ToolchainAdapter:
    name = 'base'

    def build_command(self, _: AdapterContext) -> list[str]:
        return ['echo', 'build adapter base']

    def prepare_command(self, _: AdapterContext) -> list[str]:
        return ['echo', 'prepare adapter base']
