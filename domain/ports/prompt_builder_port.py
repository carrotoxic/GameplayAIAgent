from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Protocol
from domain.models.message import Message

SystemAndUserMsg = Tuple[Message, Message]

class PromptBuilderPort(Protocol):
    """
    Hexagonal *outbound* port for building any style of prompts.
    """

    @abstractmethod
    def build_prompt(self, **kwargs) -> SystemAndUserMsg: ...