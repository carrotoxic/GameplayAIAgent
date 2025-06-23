from dataclasses import dataclass

@dataclass
class Message:
    role: str  # "system" or "user" or "assistant"
    content: str

    def __str__(self):
        return f"[{self.role}]\n{self.content}"

    def __repr__(self):
        return self.__str__()