from domain.ports import LLMPort, ParserPort, PromptBuilderPort
from domain.models import Skill, Task, Observation, Critique

class PlannerService:
    """
    Domain-pure planner.

    Responsibilities:
    ---------------
    • Build a prompt from (skillset, code_snippet, observation, task, critique).
    • Call the LLM via injected `LLMPort`.
    • Parse the reply into a domain `CodeSnippet` object.
    """

    def __init__(self, 
                 llm: LLMPort, 
                 prompt_builder: PromptBuilderPort, 
                 parser: ParserPort,
                 ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._parser = parser

    def generate_code(self, skillset: list[Skill], code_snippet: str, observation: Observation, task: Task, critique: Critique) -> str:
        system_msg, user_msg = self._prompt_builder.build_prompt(
            skillset=skillset,
            code_snippet=code_snippet,
            observation=observation,
            task=task,
            critique=critique,
        )

        llm_response = self._llm.chat([system_msg, user_msg])
        try:
            # parse LLM response to code snippet
            next_code_snippet = self._parser.parse(llm_response.content)
            return next_code_snippet
        except Exception as exc:
            raise Exception("Failed to parse LLM reply") from exc

        
    
# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder
    from infrastructure.prompts.registry import get
    from infrastructure.parsers import JSParser
    import infrastructure.prompts.builders.planner_prompt_builder
    from domain.models import Event

    planner = PlannerService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get("planner"),
        parser=JSParser(),
    )

    skillset = [
        Skill(name="mineWoodLog", 
              code="async function mineWoodLog(bot) {\n  const woodLogNames = [\"oak_log\", \"birch_log\", \"spruce_log\", \"jungle_log\", \"acacia_log\", \"dark_oak_log\", \"mangrove_log\"];\n\n  // Find a wood log block\n  const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n    return bot.findBlock({\n      matching: block => woodLogNames.includes(block.name),\n      maxDistance: 32\n    });\n  });\n  if (!woodLogBlock) {\n    bot.chat(\"Could not find a wood log.\");\n    return;\n  }\n\n  // Mine the wood log block\n  await mineBlock(bot, woodLogBlock.name, 1);\n  bot.chat(\"Wood log mined.\");\n}",
              description="Mine a wood log block"),
        Skill(name="craftWoodenPickaxe", 
              code="async function craftWoodenPickaxe(bot) {\n  const woodLogNames = [\"oak_log\", \"birch_log\", \"spruce_log\", \"jungle_log\", \"acacia_log\", \"dark_oak_log\", \"mangrove_log\"];\n\n  // Find a wood log block\n  const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n    return bot.findBlock({\n      matching: block => woodLogNames.includes(block.name),\n      maxDistance: 32\n    });\n  });\n  if (!woodLogBlock) {\n    bot.chat(\"Could not find a wood log.\");\n    return;\n  }\n\n  // Mine the wood log block\n  await mineBlock(bot, woodLogBlock.name, 1);\n  bot.chat(\"Wood log mined.\");\n}",
              description="Craft a wooden pickaxe"),
    ]

    code_snippet = "async function mineWoodLog(bot) {\n  const woodLogNames = [\"oak_log\", \"birch_log\", \"spruce_log\", \"jungle_log\", \"acacia_log\", \"dark_oak_log\", \"mangrove_log\"];\n\n  // Find a wood log block\n  const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n    return bot.findBlock({\n      matching: block => woodLogNames.includes(block.name),\n      maxDistance: 32\n    });\n  });\n  if (!woodLogBlock) {\n    bot.chat(\"Could not find a wood log.\");\n    return;\n  }\n\n  // Mine the wood log block\n  await mineBlock(bot, woodLogBlock.name, 1);\n  bot.chat(\"Wood log mined.\");\n}"

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
        Task(command="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
        Task(command="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    ]

    observation = MinecraftObservationBuilder().build(event=event, completed=tasks[:1], failed=tasks[1:])

    task = Task(
        command="Mine 1 iron ore",
        reasoning="Need iron ore",
        context="What are the blocks that I can find in the forest in Minecraft?",
    )

    critique = Critique(
        success=False,
        description="The code is not working as expected. The bot is not mining the wood log.",
    )

    code = planner.generate_code(skillset, code_snippet, observation, task, critique)
    print(code)