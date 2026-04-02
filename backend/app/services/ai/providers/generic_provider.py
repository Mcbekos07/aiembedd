from app.services.ai.providers.base import BaseAIProvider


class GenericProvider(BaseAIProvider):
    name = 'generic'

    def generate(self, model: str, prompt: str) -> str:
        return f'[generic:{model}] {prompt[:300]}'
