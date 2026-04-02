"""Registry for toolchain adapters and extension-point discovery."""

from app.core.extension_points import TOOLCHAIN_ADAPTER_KEYS
from app.services.toolchains.adapters.avr_adapter import AvrAdapter
from app.services.toolchains.adapters.custom_adapter import CustomAdapter
from app.services.toolchains.adapters.esp32_adapter import Esp32Adapter
from app.services.toolchains.adapters.mcs51_adapter import Mcs51Adapter
from app.services.toolchains.adapters.micropython_adapter import MicropythonAdapter
from app.services.toolchains.adapters.rp2040_adapter import Rp2040Adapter
from app.services.toolchains.adapters.stm32_adapter import Stm32Adapter
from app.services.toolchains.adapters.verilog_adapter import VerilogAdapter


class ToolchainRegistry:
    def __init__(self) -> None:
        self._items = {
            'stm32': Stm32Adapter(),
            'avr': AvrAdapter(),
            'esp32': Esp32Adapter(),
            'rp2040': Rp2040Adapter(),
            'mcs-51': Mcs51Adapter(),
            'micropython': MicropythonAdapter(),
            'verilog': VerilogAdapter(),
            'custom': CustomAdapter(),
        }

    def get(self, platform: str):
        return self._items.get(platform.lower(), self._items['custom'])

    def list_names(self) -> list[str]:
        return sorted(self._items.keys())

    def extension_points(self) -> tuple[str, ...]:
        return TOOLCHAIN_ADAPTER_KEYS
