from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
from domain.models import Message

SystemAndUserMsg = Tuple[Message, Message]

class PromptBuilderPort(ABC):
    """
    Hexagonal *outbound* port for building any style of prompts.
    """

    @abstractmethod
    def build_prompt(self, **kwargs) -> SystemAndUserMsg: ...