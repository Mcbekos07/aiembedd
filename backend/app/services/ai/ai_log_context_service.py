from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService


class AILogContextService:
    def extract_levels(self, raw_log: str) -> dict[str, object]:
        events = ImportantLogService().extract_events(raw_log, limit=180)
        return LogSummaryService().compress(raw_log, events)

    def extract(self, raw_log: str) -> str:
        levels = self.extract_levels(raw_log)
        return str(levels.get('compressed_ai_context', ''))
