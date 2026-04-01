class AIFlashAssistService:
    def explain_flash_error(self, summary: str) -> str:
        return f'Объяснение flash ошибки:\n{summary[:300]}'
