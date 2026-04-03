class BuildSummaryService:
    ERROR_MARKERS = ('error:', 'undefined reference', 'fatal', 'Traceback')

    def summarize(self, raw_log: str) -> list[str]:
        lines = raw_log.splitlines()
        return [line for line in lines if any(marker in line.lower() for marker in self.ERROR_MARKERS)][:30]
