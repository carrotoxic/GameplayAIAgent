from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models import Message, CodeSnippet
from infrastructure.utils import load_prompt
from infrastructure.prompts.registry import register

@register("minecraft", "skill_description")
class SkillDescriptionPromptBuilder(_BasePromptBuilder):
    """SkillService uses this prompt builder to generate a description for a skill"""

    def _system_header(self, **kw) -> Message:
        return Message(
            role="system",
            content=load_prompt("minecraft", "skill", "description")
        ) 

    def _compose_user(
        self,
        code_snippet: CodeSnippet
    ) -> Message:
        return Message(
            role="user",
            content=f"{code_snippet.code}\n\nThe main function is `{code_snippet.function_name}`."
        )