from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models import Message
from infrastructure.utils import load_prompt
from infrastructure.prompts.registry import register

@register("minecraft", "planner")
class PlannerPromptBuilder(_BasePromptBuilder):
    """PlannerService uses this prompt builder"""

    def _system_header(self, **kw) -> Message:
        skillset = kw["skillset"]
        system_base = load_prompt("minecraft", "planner", "base")

        skillset_code_txt = ""
        for skill in skillset:
            skillset_code_txt += f"{skill.code}\n"
        skillset_code_txt = skillset_code_txt.rstrip("\n")

        response_format = load_prompt("minecraft", "planner", "format")

        system_header = system_base.format(programs=skillset_code_txt, response_format=response_format)

        return Message(
            role="system",
            content=system_header
        )

    def _compose_user(
        self,
        **kw
    ) -> Message:
        code_snippet = kw["code_snippet"]
        observation = kw["observation"]
        task = kw["task"]
        critique = kw["critique"]

        return Message(
            role="user",
            content=(
                f"Code from the last round: \n{code_snippet}\n"
                f"{observation}\n"
                f"Task: {task.command}\n"
                f"Context: \n[{task.context}]\n"
                f"Critique: {critique}"
            )
        )



# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder
    from infrastructure.prompts.registry import get
    from domain.models import CodeSnippet, Task, Observation
    from domain.services.planner import PlannerService

    compose_user = PlannerPromptBuilder()._compose_user(
        code_snippet=CodeSnippet(
            function_name="testMoveAgent",
            main_function_code="""
            async function testMoveAgent(bot) {
                bot.chat("Movement test finished.");
            }
            """,
            execution_code="await testMoveAgent(bot);"
        ),
        observation=Observation(
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
            error_message="Evaluation error: Runtime error: Took to long to decide path to goal!",
            chat_message="Explore success.",
        ),
        task=Task(
            command="Move the agent to the goal position.",
            context="The agent is at the starting position.",
            reasoning="The agent is at the starting position.",
        ),
        critique="The agent is not moving.",
    )

    print(compose_user.content)