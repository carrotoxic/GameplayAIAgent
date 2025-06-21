from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol, List
from domain.models.observation import Observation
from domain.models.event import Event
from domain.models.task import Task

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