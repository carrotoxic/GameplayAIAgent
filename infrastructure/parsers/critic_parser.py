from __future__ import annotations
import json
import re
from domain.ports.parser_port import ParserPort

class CriticParser(ParserPort):
    """
    Parse an LLM reply that returns JSON like:

    {
        "reasoning": "Based on the information...",
        "success": true,
        "critique": "The agent didn't complete the task because it ran out of resources."
    }

    Returns:
        tuple[bool, str]: A tuple containing success and critique string.
    """

    def parse(self, text: str) -> tuple[bool, str]:
        # ―― strip Markdown fences like ```json … ``` or ``` … ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        json_str = match.group(1) if match else text.strip()
        print(f"CriticParser: json_str: {json_str}")
        try:
            data = json.loads(json_str)
            return bool(data["success"]), data.get("critique", "")
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
