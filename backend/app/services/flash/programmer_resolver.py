"""Resolves default flasher/programmer by project platform."""


class ProgrammerResolver:
    DEFAULTS = {
        'stm32': 'stlink',
        'esp32': 'esptool',
        'avr': 'avrdude',
        'rp2040': 'openocd',
    }

    def resolve(self, platform: str, requested: str | None) -> str:
        if requested:
            return requested
        return self.DEFAULTS.get(platform.lower(), 'custom')
