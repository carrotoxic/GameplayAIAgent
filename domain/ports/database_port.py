from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Sequence
from domain.models import Skill


class DatabasePort(ABC):
    """
    Hexagonal *outbound* port for persisting data.
    """
    # ---------- Count ----------
    @abstractmethod
    def count(self) -> int:
        """Return the number of items in the database."""

    # ---------- Query ----------
    @abstractmethod
    def lookup(self, key: str) -> str | None:
        """If the key is in the database, return the value. If not, return None."""

    # ---------- Command ----------
    @abstractmethod
    def store(self, key: str, value: str) -> None:
        """Store a new query in the database."""

    @abstractmethod
    async def add(self, documents: Sequence[Skill]):
        pass

    @abstractmethod
    async def query(self, query: str) -> Sequence[Skill]:
        pass

    @abstractmethod
    async def clear(self) -> None:
        pass
