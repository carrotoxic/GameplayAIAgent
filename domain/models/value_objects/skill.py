from dataclasses import dataclass
from typing import Optional

@dataclass
class Skill:
    name: str
    code: str
    description: Optional[str] = None