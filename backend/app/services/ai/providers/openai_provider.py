from app.services.ai.providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    name = 'openai'

    def generate(self, model: str, prompt: str) -> str:
        return f'[openai:{model}] {prompt[:300]}'
