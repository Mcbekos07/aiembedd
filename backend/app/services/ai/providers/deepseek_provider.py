from app.services.ai.providers.base import BaseAIProvider


class DeepseekProvider(BaseAIProvider):
    name = 'deepseek'

    def generate(self, model: str, prompt: str) -> str:
        return f'[deepseek:{model}] {prompt[:300]}'
