class PortResolverService:
    def list_ports(self) -> list[str]:
        return ['/dev/ttyUSB0', '/dev/ttyACM0']
