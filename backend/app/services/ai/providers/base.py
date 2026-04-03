from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    name = 'base'

    @abstractmethod
    def generate(self, model: str, prompt: str) -> str:
        raise NotImplementedError
