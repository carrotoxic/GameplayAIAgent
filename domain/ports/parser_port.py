from __future__ import annotations
from abc import abstractmethod
from typing import List

class ParserPort:
    """parse text into a list of objects"""

    @abstractmethod
    def parse(self, text: str) -> List[str]:
        pass
