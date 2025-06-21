from __future__ import annotations
import re
from typing import List
from domain.ports.parser_port import ParserPort
from domain.models.task import Task

_REASONING_LINE = re.compile(r"^\s*Reasoning\s*:\s*(.+?)\s*$")
_TASK_LINE = re.compile(r"^\s*Task\s*:\s*(.+?)\s*$")

class TaskParser(ParserPort):
    """
    Parse a LLM reply like:
    
        Reasoning: Based on the information ....
        Task: Mine 1 iron ore

    and return a Task object.
    """

    def parse(self, text: str) -> Task:
        reasoning = ""
        task = ""
        for line in text.splitlines():
            if _REASONING_LINE.match(line):
                reasoning = _REASONING_LINE.match(line).group(1).strip()
            if _TASK_LINE.match(line):
                task = _TASK_LINE.match(line).group(1).strip()
        return Task(task=task, reasoning=reasoning, context="")


if __name__ == "__main__":
    parser = TaskParser()
    text = "Reasoning: Based on the information ....\nTask: Mine 1 iron ore"
    print(parser.parse(text))