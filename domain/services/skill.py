from typing import List
from domain.ports import LLMPort, ParserPort, DatabasePort, PromptBuilderPort
from domain.models import Skill, Task

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
        skill_description_prompt_builder: PromptBuilderPort,
        parser: ParserPort,
        database: DatabasePort,
        retrieval_top_k: int = 5,
    ):
        self._llm = llm
        self._skill_description_prompt_builder = skill_description_prompt_builder
        self._parser = parser
        self._database = database
        self._retrieval_top_k = retrieval_top_k

        self.skills = {}

    def add_skill(self, skill: Skill) -> None:
        """
        Add a new skill to the skill library.
        """
        # Generate skill description (e.g. summarization)
        description = self._generate_description(skill)
        skill_with_description = Skill(
            name=skill.name,
            code=skill.code,
            description=description,
        )
        self._database.store(texts=[description], metadatas=[{"skill": skill.name}], ids=[skill.name])
        self.skills[skill.name] = skill_with_description
        assert self._database.count() == len(
            self.skills
        ), "database is not synced with skills"

    def retrieve_skillset(self, task: Task) -> List[Skill]:
        """
        Retrieve top-k relevant skills based on the task.
        """
        query = task.context
        skills = self._database.similarity_search(query=query, k=self._retrieval_top_k)
        return skills

    def _generate_description(self, skill: Skill) -> str:
        """
        Generate a description for a skill.
        """
        system_msg, user_msg = self._skill_description_prompt_builder.build_prompt(
            skill=skill
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
    from infrastructure.parsers.task_parser import TaskParser
    import infrastructure.prompts.builders.skill_description_prompt_builder

    skill = Skill(
        name="mineWoodLog",
        code="async function mineWoodLog(bot) {\n  const woodLogNames = [\"oak_log\", \"birch_log\", \"spruce_log\", \"jungle_log\", \"acacia_log\", \"dark_oak_log\", \"mangrove_log\"];\n\n  // Find a wood log block\n  const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {\n    return bot.findBlock({\n      matching: block => woodLogNames.includes(block.name),\n      maxDistance: 32\n    });\n  });\n  if (!woodLogBlock) {\n    bot.chat(\"Could not find a wood log.\");\n    return;\n  }\n\n  // Mine the wood log block\n  await mineBlock(bot, woodLogBlock.name, 1);\n  bot.chat(\"Wood log mined.\");\n}",
        description="async function mineWoodLog(bot) {\n    // The function is about mining a single wood log block. It searches for a wood log block by exploring the environment until it finds one of the seven types of wood logs. If a wood log block is found, it is mined and a success message is sent. If no wood log block is found, a failure message is sent.\n}",
    )
    
    skill_service = SkillService(
        llm=LangchainOllamaLLM(),
        skill_description_prompt_builder=get("skill_description"),
        parser=TaskParser(),
        database=ChromaDatabase(collection_name="skill_library"),
    )

    skill_service.add_skill(skill)
    print(skill_service.skills)