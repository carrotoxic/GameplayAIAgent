from abc import ABC, abstractmethod
from typing import Sequence
from domain.models import Message

class LLMPort(ABC):
    """Hexagonal *outbound* port for any chat-style LLM."""
    @abstractmethod
    async def chat(self, messages: Sequence[Message]) -> Message:
        pass
