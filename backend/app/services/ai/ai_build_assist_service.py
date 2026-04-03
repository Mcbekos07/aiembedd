class AIBuildAssistService:
    def explain_error(self, summary: str) -> str:
        return f'Объяснение build ошибки:\n{summary[:300]}'
