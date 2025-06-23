from __future__ import annotations
import json
from typing import Any
from domain.ports.parser_port import ParserPort
from domain.models import Critique


class CriticParser(ParserPort):
    """
    Parse an LLM reply that returns JSON like:

    {
        "reasoning": "Based on the information...",
        "success": true,
        "critique": "The agent didn't complete the task because it ran out of resources."
    }

    Returns:
        Critique: A domain model containing success and critique string.
    """

    def parse(self, text: str) -> Critique:
        try:
            data = json.loads(text)
            return Critique(
                success=bool(data["success"]),
                description=data.get("critique", "")
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid LLM response format: {e}")


if __name__ == "__main__":
    parser = CriticParser()
    llm_output = """
    {
        "reasoning": "The bot attempted the task but encountered lava.",
        "success": false,
        "critique": "The agent should have checked the surroundings before digging."
    }
    """
    print(parser.parse(llm_output))
