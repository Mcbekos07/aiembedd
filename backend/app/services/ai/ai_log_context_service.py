from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService


class AILogContextService:
    def extract(self, raw_log: str) -> str:
        important = ImportantLogService().extract(raw_log)
        summary = LogSummaryService().summarize(important)
        return '\n'.join(important + ([summary] if summary else []))
