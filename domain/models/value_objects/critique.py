from dataclasses import dataclass

@dataclass(frozen=True)
class Critique:
    success: bool
    description: str