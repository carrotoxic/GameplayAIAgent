from dataclasses import dataclass

@dataclass
class Task:
    task: str             # One-liner command (e.g., "Mine 1 iron ore")
    reasoning: str        # LLM's reasoning explaining why this task
    context: str          # Internal/external knowledge, tutorials, or tips