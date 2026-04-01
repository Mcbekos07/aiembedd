from app.services.ai.providers.base import BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    name = 'anthropic'

    def generate(self, model: str, prompt: str) -> str:
        return f'[anthropic:{model}] {prompt[:300]}'
