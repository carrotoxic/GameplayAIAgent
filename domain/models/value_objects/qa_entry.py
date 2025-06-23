from dataclasses import dataclass

@dataclass
class QAEntry:
    question: str
    answer: str

    def __str__(self) -> str:
        return f"Question: {self.question}\nAnswer: {self.answer}"