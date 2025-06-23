from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models.message import Message
from domain.models.skill import Skill
from infrastructure.prompts.utils import load_prompt
from infrastructure.prompts.registry import register

@register("skill_description")
class SkillDescriptionPromptBuilder(_BasePromptBuilder):
    """SkillService uses this prompt builder to generate a description for a skill"""

    def _system_header(self, **kw) -> Message:
        return Message(
            role="system",
            content=load_prompt("skill", "description")
        ) 

    def _compose_user(
        self,
        skill: Skill
    ) -> Message:
        return Message(
            role="user",
            content=f"{skill.code}\n\nThe main function is `{skill.name}`."
        )