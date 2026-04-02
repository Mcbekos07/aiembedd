"""AI provider registry with explicit extension-point exposure."""

from app.core.extension_points import AI_PROVIDER_KEYS
from app.services.ai.providers.anthropic_provider import AnthropicProvider
from app.services.ai.providers.deepseek_provider import DeepseekProvider
from app.services.ai.providers.generic_provider import GenericProvider
from app.services.ai.providers.openai_provider import OpenAIProvider


class AIProviderService:
    def __init__(self) -> None:
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'deepseek': DeepseekProvider(),
            'generic': GenericProvider(),
        }

    def get(self, name: str):
        return self.providers.get(name, self.providers['generic'])

    def extension_points(self) -> tuple[str, ...]:
        return AI_PROVIDER_KEYS
