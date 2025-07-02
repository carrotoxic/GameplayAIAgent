from typing import List, Sequence, Optional
from ..ports import LLMPort, PromptBuilderPort
from ..models import Task, CodeSnippet, Observation, Skill
from ..ports.parser_port import ParserPort

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
                 max_code_generation_tries: int = 5,
                 ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._parser = parser
        self._max_code_generation_tries = max_code_generation_tries

    async def generate_code(self, 
        skillset: Sequence[Skill], 
        code_snippet: Optional[CodeSnippet],
        observation: Observation, 
        task: Task, 
        critique: Optional[str]) -> CodeSnippet:
        
        system_msg, user_msg = self._prompt_builder.build_prompt(
            skillset=skillset,
            code_snippet=code_snippet,
            observation=observation,
            task=task,
            critique=critique
        )
        response = await self._llm.chat(messages=[system_msg, user_msg])
        code_snippet = self._parser.parse(response.content)
        return code_snippet, response.content
    
# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder
    from infrastructure.prompts.registry import get
    from infrastructure.parsers import JSParser

    planner = PlannerService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get("minecraft", "planner"),
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

    # code_snippet = "async function mineWoodLog(bot) {\n  const woodLogNames = [\"oak_log\", \"birch_log\", \"spruce_log\", \"jungle_log\", \"acacia_log\", \"dark_oak_log\", \"mangrove_log\"];\n\n  // Find a wood log block\n  const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n    return bot.findBlock({\n      matching: block => woodLogNames.includes(block.name),\n      maxDistance: 32\n    });\n  });\n  if (!woodLogBlock) {\n    bot.chat(\"Could not find a wood log.\");\n    return;\n  }\n\n  // Mine the wood log block\n  await mineBlock(bot, woodLogBlock.name, 1);\n  bot.chat(\"Wood log mined.\");\n}"


    # tasks = [
    #     Task(command="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
    #     Task(command="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    # ]

    # observation = MinecraftObservationBuilder().build(event=event, completed=tasks[:1], failed=tasks[1:])

    # task = Task(
    #     command="Mine 1 iron ore",
    #     reasoning="Need iron ore",
    #     context="What are the blocks that I can find in the forest in Minecraft?",
    # )

    # critique = "The code is not working as expected. The bot is not mining the wood log."

    # code = planner.generate_code(skillset, code_snippet, observation, task, critique)
    # print(code)