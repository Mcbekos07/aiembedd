from app.services.ai.ai_provider_service import AIProviderService


class AIRouterService:
    def route(self, provider: str, model: str, prompt: str) -> str:
        engine = AIProviderService().get(provider)
        return engine.generate(model, prompt)
