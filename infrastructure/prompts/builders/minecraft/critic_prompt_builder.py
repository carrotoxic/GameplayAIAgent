from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models import Message, Task, Observation
from infrastructure.utils import load_prompt
from infrastructure.prompts.registry import register

@register("minecraft", "critic")
class CriticPromptBuilder(_BasePromptBuilder):
    """CriticService uses this prompt builder"""

    def _system_header(self, **kw) -> Message:
        return Message(
            role="system",
            content=load_prompt("minecraft", "critic", "base")
        )

    def _compose_user(self, **kw) -> Message:
        observation = kw["observation"]
        task = kw["task"]

        return Message(
            role="user",
            content=(
                f"{observation}\n\n"
                f"Task: {task.command}\n\n"
                f"Context: {task.context}"
            )
        )


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    from domain.models import Task, Observation

    task = Task(command="Mine 1 wood log", context="Tutorial", reasoning="Need wood")

    observation = Observation(
        biome="forest",
        time="day",
        nearby_blocks="grass, dirt, stone, oak_log",
        other_blocks="iron_ore",
        nearby_entities="cow",
        health="18.5/20",
        hunger="15.0/20",
        position={"x": 10.5, "y": 64.0, "z": -5.2},
        equipment="leather_helmet",
        inventory="oak_log: 3, wooden_pickaxe: 1",
        chests={"Chest 1": "iron_ingot: 8", "Chest 2": "iron_ingot: 8"},
        error_message="Evaluation error: Runtime error: Took to long to decide path to goal!",
        chat_message="Explore success.",
    )

    critic_builder = CriticPromptBuilder()
    sys_msg, user_msg = critic_builder.build_prompt(observation=observation, task=task)
    print("-------system message-------")
    print(sys_msg)
    print("-------user message-------")
    print(user_msg)
