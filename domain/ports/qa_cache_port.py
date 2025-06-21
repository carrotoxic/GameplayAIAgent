from __future__ import annotations
from abc import ABC, abstractmethod


class QACachePort(ABC):
    """
    Hexagonal *outbound* port for persisting QA pairs.
    """

    # ---------- Query ----------
    @abstractmethod
    def lookup(self, question: str) -> str | None:
        """If the question is in the cache, return the answer. If not, return None."""

    # ---------- Command ----------
    @abstractmethod
    def store(self, question: str, answer: str) -> None:
        """Store a new QA pair in the cache."""
