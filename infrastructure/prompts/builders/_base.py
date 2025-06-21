from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
from domain.ports.prompt_builder_port import PromptBuilderPort, Message

SystemAndUserMsg = Tuple[Message, Message]


class _BasePromptBuilder(PromptBuilderPort, ABC):
    """
    (1) Observation -> (2) system -> (3) user
    Hooks to implement each variation.
    """

    # ----------------- final method -----------------
    def build_prompt(self, **kw) -> SystemAndUserMsg:
        sys_msg = self._system_header()
        user_msg = self._compose_user(**kw)
        return sys_msg, user_msg

    # ----------------- hooks --------------------------
    @abstractmethod
    def _system_header(self) -> Message: ...

    @abstractmethod
    def _compose_user(
        self,
        **kw,
    ) -> Message: ...
