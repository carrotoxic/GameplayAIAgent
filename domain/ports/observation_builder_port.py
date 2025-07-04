from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from domain.models import Observation

class ObservationBuilderPort(Protocol):
    """
    Hexagonal *outbound* port for building any style of prompts.
    """

    @abstractmethod
    def build(self, *,event: dict) -> Observation: ...