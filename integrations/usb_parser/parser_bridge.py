from integrations.usb_parser.adapter import USBParserAdapter


class USBParserBridge:
    def list_devices(self) -> list[dict[str, str]]:
        return USBParserAdapter().parse()
