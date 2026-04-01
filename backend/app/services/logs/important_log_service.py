class ImportantLogService:
    PATTERNS = ('error:', 'linker', 'failed', 'timeout', 'warning')

    def extract(self, raw: str) -> list[str]:
        lines = raw.splitlines()
        return [line for line in lines if any(p in line.lower() for p in self.PATTERNS)][:40]
