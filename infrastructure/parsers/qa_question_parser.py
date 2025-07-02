from __future__ import annotations
import re
from typing import List
from domain.ports.parser_port import ParserPort

_QUESTION_LINE = re.compile(r"^\s*Question\s*\d+\s*:\s*(.+?)\s*$")

class QAQuestionParser(ParserPort):
    """
    Parse a LLM reply like:
    
        Reasoning: As I'm in a forest biome and ...
        Question 1: How can I obtain more oak logs?
        Concept 1: oak_log
        Question 2: ...
        Concept 2: ...

    and return only the list of questions.
    """

    def parse(self, text: str) -> List[str]:
        questions: list[str] = []
        for line in text.splitlines():
            question_match = _QUESTION_LINE.match(line)
            if question_match:
                questions.append(question_match.group(1).strip())
        return questions



if __name__ == "__main__":
    parser = QAQuestionParser()
    text = """
    Reasoning: As I'm in a forest biome and ...
    Question 1: How can I obtain more oak logs?
    Concept 1: oak_log
    Question 2: ...
    Concept 2: ...
    """
    print(parser.parse(text))