from typing import List
from domain.ports import LLMPort, DatabasePort, PromptBuilderPort
from domain.models import Skill, Task, CodeSnippet

class SkillService:
    """
    Domain-pure skill library.

    Responsibilities:
    ---------------
    • Add a new skill to the skill library.
    • Retrieve skillset relevant to a given task.
    ---------------
    """

    def __init__(
        self,
        llm: LLMPort,
        prompt_builder: PromptBuilderPort,
        database: DatabasePort,
        resume: bool = False
    ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._database = database
        
        if not resume:
            self._database.clear()  # clear vector DB
            self.skills = {}
        # else:
        #     self.skills = self._database.load()

    def add_skill(self, code_snippet: CodeSnippet) -> None:
        """
        Add a new skill to the skill library.
        """
        # Generate skill description (e.g. summarization)
        description = self._generate_description(code_snippet)
        skill_with_description = Skill(
            name=code_snippet.function_name,
            code=code_snippet.code,
            description=description,
        )
        self._database.store(texts=[description], metadatas=[{"skill": skill_with_description.name}], ids=[skill_with_description.name])
        self.skills[skill_with_description.name] = skill_with_description
        assert self._database.count() == len(
            self.skills
        ), "database is not synced with skills"

    def retrieve_skillset(self, task: Task) -> List[Skill]:
        """
        Retrieve relevant skills based on the task.
        """
        query = task.context
        skills = self._database.lookup(query=query)
        return skills

    def _generate_description(self, code_snippet: str) -> str:
        """
        Generate a description for a skill.
        """
        system_msg, user_msg = self._prompt_builder.build_prompt(
            code_snippet=code_snippet
        )
        llm_response = self._llm.chat([system_msg, user_msg])
        return llm_response.content
    


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":

    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.adapters.database.chroma_database import ChromaDatabase
    from infrastructure.prompts.registry import get

    skill_service = SkillService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get("minecraft", "skill_description"),
        database=ChromaDatabase(collection_name="skill_library"),
        resume=False
    )

    skill_service.add_skill(CodeSnippet(
        function_name="mineWoodLog",
        code="async function mineWoodLog(bot) {\n  const woodLogNames = [\"oak_log\", \"birch_log\", \"spruce_log\", \"jungle_log\", \"acacia_log\", \"dark_oak_log\", \"mangrove_log\"];\n\n  // Find a wood log block\n  const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n    return bot.findBlock({\n      matching: block => woodLogNames.includes(block.name),\n      maxDistance: 32\n    });\n  });\n  if (!woodLogBlock) {\n    bot.chat(\"Could not find a wood log.\");\n    return;\n  }\n\n  // Mine the wood log block\n  await mineBlock(bot, woodLogBlock.name, 1);\n  bot.chat(\"Wood log mined.\");\n}"
    ))

    print(skill_service.skills)