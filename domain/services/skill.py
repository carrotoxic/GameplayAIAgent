from typing import List, Sequence
from ..ports import LLMPort, DatabasePort, PromptBuilderPort
from ..models import Skill, Task, CodeSnippet

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
    ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._database = database

    async def add_skill(self, skill: Skill):
        await self._database.add([skill])

    async def retrieve_skillset(self, task: Task) -> Sequence[Skill]:
        return await self._database.query(task.command)

    def _generate_description(self, code_snippet: str) -> str:
        """
        Generate a description for a skill.
        """
        system_msg, user_msg = self._prompt_builder.build_prompt(
            code_snippet=code_snippet
        )
        llm_response = self._llm.chat([system_msg, user_msg])
        return llm_response.content
    
    async def clear(self) -> None:
        await self._database.clear()

    def show_all(self) -> None:
        self._database.show_all()
    
    async def describe_skill(self, code: CodeSnippet) -> Skill:
        system_msg, user_msg = self._prompt_builder.build_prompt(code_snippet=code)
        response = await self._llm.chat(messages=[system_msg, user_msg])
        return Skill(code=code.main_function_code, name=code.function_name, description=response.content)

# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    # This test block is outdated and has been removed to prevent confusion.
    # It was not compatible with the recent async changes and was using
    # domain models incorrectly.
    pass