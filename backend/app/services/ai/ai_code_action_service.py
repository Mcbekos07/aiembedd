class AICodeActionService:
    def suggest_code(self, request: str) -> str:
        return f'// suggestion\n// {request}'

    def generate_patch(self, request: str) -> str:
        return f'PATCH:\n{request}'
