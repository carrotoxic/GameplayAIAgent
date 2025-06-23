from dataclasses import dataclass

@dataclass
class Skill:
    name: str
    code: str
    description: str

    def __str__(self) -> str:
        return f"code={self.code}, description={self.description}"