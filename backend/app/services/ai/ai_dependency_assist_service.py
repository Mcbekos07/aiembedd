class AIDependencyAssistService:
    def install_plan(self, issues: str) -> str:
        return f'План установки зависимостей:\n{issues[:200]}'
