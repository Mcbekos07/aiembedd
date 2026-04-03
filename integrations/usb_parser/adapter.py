class USBParserAdapter:
    def parse(self) -> list[dict[str, str]]:
        return [{'id': 'parser-dev-1', 'vendor': 'MockVendor', 'product': 'MockProduct'}]
