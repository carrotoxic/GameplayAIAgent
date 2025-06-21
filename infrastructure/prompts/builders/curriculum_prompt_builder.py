from __future__ import annotations
from typing import Sequence
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models.message import Message
from domain.models.observation import Observation
from domain.models.qa_entry import QAEntry
from infrastructure.prompts.utils import load_prompt
from infrastructure.prompts.registry import register

@register("curriculum")
class CurriculumPromptBuilder(_BasePromptBuilder):
    """CurriculumService uses this prompt builder"""

    def _system_header(self) -> Message:
        return Message(
            role="system",
            content=load_prompt("curriculum", "base")
        )

    def _compose_user(
        self,
        qa_entries: Sequence[QAEntry],
        observation: Observation
    ) -> Message:
        qa_txt = ""
        if qa_entries:
            for idx, qa_entry in enumerate(qa_entries):
                qa_txt += f"Question {idx+1}: {qa_entry.question}\nAnswer: {qa_entry.answer}\n"
            qa_txt = qa_txt.rstrip("\n")

        return Message(
            role="user",
            content=f"{qa_txt}\n\n{observation}"
        )


if __name__ == "__main__":
    from domain.models.event import Event
    from domain.models.task import Task
    from infrastructure.prompts.builders.minecraft_observation_builder import MinecraftObservationBuilder

    curriculum_builder = CurriculumPromptBuilder()
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
        chests="Chest 1: iron_ingot: 8",
    )

    tasks = [
        Task(task="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
        Task(task="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    ]

    qa_entries = [
        QAEntry(question="What are the blocks that I can find in the forest in Minecraft?", answer="The blocks that I can find in the forest in Minecraft are grass, dirt, stone, and oak_log."),
        QAEntry(question="What are the items that I can find in the forest in Minecraft?", answer="The items that I can find in the forest in Minecraft are oak_log, wooden_pickaxe, and iron_ingot."),
        QAEntry(question="What are the mobs that I can find in the forest in Minecraft?", answer="The mobs that I can find in the forest in Minecraft are cow."),
    ]

    obs = obs_builder.build(event=event, completed=tasks[:1], failed=tasks[1:])

    sys_msg, user_msg = curriculum_builder.build_prompt(qa_entries=qa_entries, observation=obs)
    print("-------system message-------")
    print(sys_msg)
    print("-------user message-------")
    print(user_msg)