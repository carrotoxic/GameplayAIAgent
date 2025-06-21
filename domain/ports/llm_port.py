from abc import ABC, abstractmethod
from typing import Sequence
from domain.models.message import Message

class LLMPort(ABC):
    """Hexagonal *outbound* port for any chat-style LLM."""
    @abstractmethod
    def chat(self, messages: Sequence[Message]) -> str: ...
