from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models import Task, Observation, Message
from infrastructure.prompts.utils import load_prompt
from infrastructure.prompts.registry import register
from typing import List

@register("qa_question")
class QAPromptBuilder(_BasePromptBuilder):
    """QAService uses this prompt builder"""

    def _system_header(self, **kw) -> Message:
        return Message(
            role="system",
            content=load_prompt("curriculum", "qa_question")
        )

    def _compose_user(self, **kw) -> Message:
        observation = kw['observation']
        completed_tasks = kw['completed_tasks']
        failed_tasks = kw['failed_tasks']

        return Message(
            role="user",
            content=f"{observation}\n\n"
            f"Completed tasks: {', '.join(task.command for task in completed_tasks)}\n\n"
            f"Failed tasks: {', '.join(task.command for task in failed_tasks)}"
        )



# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    from domain.models import Event, Task
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder

    qa_builder = QAPromptBuilder()
    obs_builder = MinecraftObservationBuilder()

    event = Event(
        position={"x": 10.5, "y": 64.0, "z": -5.2},
        inventory={"oak_log": 3, "wooden_pickaxe": 1},
        health=18.5,
        hunger=15.0,
        biome="forest",
        nearby_blocks=["grass", "dirt", "stone", "oak_log"],
        nearby_entities={"cow": 5.0},
        time="day",
        other_blocks="iron_ore",
        equipment={"helmet": "leather_helmet"},
        chests={"Chest 1": "iron_ingot: 8", "Chest 2": "iron_ingot: 8"},
    )

    tasks = [
        Task(command="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
        Task(command="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    ]

    obs = obs_builder.build(event=event)

    sys_msg, user_msg = qa_builder.build_prompt(observation=obs, completed_tasks=tasks[:1], failed_tasks=tasks[1:])
    print("-------system message-------")
    print(sys_msg)
    print("-------user message-------")
    print(user_msg)