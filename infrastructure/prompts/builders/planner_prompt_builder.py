from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models import Message, Skill, Observation, Task, Critique
from infrastructure.prompts.utils import load_prompt
from infrastructure.prompts.registry import register

@register("planner")
class PlannerPromptBuilder(_BasePromptBuilder):
    """PlannerService uses this prompt builder"""

    def _system_header(self, **kw) -> Message:
        skillset = kw["skillset"]
        system_base = load_prompt("planner", "base")

        skillset_code_txt = ""
        for skill in skillset:
            skillset_code_txt += f"{skill.code}\n"
        skillset_code_txt = skillset_code_txt.rstrip("\n")

        response_format = load_prompt("planner", "format")

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
                f"Code from the last round: \n{code_snippet}\n\n"
                f"{observation}\n"
                f"Task: {task.command}\n"
                f"Context: {task.context}\n"
                f"Critique: {critique.description}"
            )
        )
