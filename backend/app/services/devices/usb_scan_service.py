class USBScanService:
    def scan(self) -> list[dict[str, str]]:
        return [
            {'id': 'mock-usb-1', 'vendor': 'STMicroelectronics', 'product': 'ST-Link'},
            {'id': 'mock-usb-2', 'vendor': 'Espressif', 'product': 'USB JTAG/serial'},
        ]
