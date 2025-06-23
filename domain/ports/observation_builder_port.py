from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol, List
from domain.models import Observation, Event, Task

class ObservationBuilderPort(Protocol):
    """
    Hexagonal *outbound* port for building any style of prompts.
    """

    @abstractmethod
    def build(
        self,
        *,
        event: Event,
        completed: List[Task],
        failed: List[Task],
    ) -> Observation: ...