"""Registry for flasher backends used by flash workflows."""

from app.core.extension_points import FLASHER_KEYS
from app.services.toolchains.flashers.avrdude_flasher import AvrdudeFlasher
from app.services.toolchains.flashers.esptool_flasher import EsptoolFlasher
from app.services.toolchains.flashers.openocd_flasher import OpenocdFlasher
from app.services.toolchains.flashers.stlink_flasher import StlinkFlasher


class FlasherRegistry:
    def __init__(self) -> None:
        self._flashers = {
            'stlink': StlinkFlasher(),
            'esptool': EsptoolFlasher(),
            'avrdude': AvrdudeFlasher(),
            'openocd': OpenocdFlasher(),
        }

    def get(self, flasher: str):
        return self._flashers.get(flasher)

    def extension_points(self) -> tuple[str, ...]:
        return FLASHER_KEYS
