"""Aggregates hardware discovery signals from scanner extension points."""

from app.core.extension_points import DEVICE_SCANNER_KEYS
from integrations.usb_parser.parser_bridge import USBParserBridge

from app.services.devices.port_resolver_service import PortResolverService
from app.services.devices.usb_scan_service import USBScanService


class DeviceService:
    def list_devices(self) -> dict[str, list[dict[str, str]] | list[str]]:
        usb_scan = USBScanService().scan()
        parser_items = USBParserBridge().list_devices()
        ports = PortResolverService().list_ports()
        return {'usb_scan': usb_scan, 'usb_parser': parser_items, 'ports': ports}

    def extension_points(self) -> tuple[str, ...]:
        return DEVICE_SCANNER_KEYS

    def choose_default_port(self, preferred: str = '') -> str:
        if preferred:
            return preferred
        ports = self.list_devices().get('ports')
        if isinstance(ports, list) and ports:
            return str(ports[0])
        return '/dev/ttyUSB0'
