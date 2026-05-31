from abc import ABC, abstractmethod
from typing import List, Optional


class BaseAgent(ABC):

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        n: int = 1,
        temperature: float = 1.0,
        max_tokens: int = 32768,
        top_p: float = 0.95,
    ) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    async def generate_batch(
        self,
        prompts: List[str],
        temperature: float = 1.0,
        max_tokens: int = 32768,
        top_p: float = 0.95,
    ) -> List[str]:
        raise NotImplementedError
