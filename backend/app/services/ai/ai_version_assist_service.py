class AIVersionAssistService:
    def create_message(self, changes: str) -> str:
        return f'Версия: обновления по изменениям: {changes[:200]}'
