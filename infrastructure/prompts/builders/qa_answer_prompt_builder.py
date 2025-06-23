from __future__ import annotations
from infrastructure.prompts.builders._base import _BasePromptBuilder
from domain.models.message import Message
from infrastructure.prompts.utils import load_prompt
from infrastructure.prompts.registry import register

@register("qa_answer")
class QAPromptBuilder(_BasePromptBuilder):
    """QAService uses this prompt builder"""

    def _system_header(self, **kw) -> Message:
        return Message(
            role="system",
            content=load_prompt("curriculum", "qa_answer")
        )

    def _compose_user(
        self,
        question: str,
    ) -> Message:
        return Message(
            role="user",
            content=f"{question}"
        )


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    qa_builder = QAPromptBuilder()

    questions = f"What are the blocks that I can find in the forest in Minecraft?\nWhat are the items that I can find in the forest in Minecraft?\nWhat are the mobs that I can find in the forest in Minecraft?"

    sys_msg, user_msg = qa_builder.build_prompt(question=questions)
    print("-------system message-------")
    print(sys_msg)
    print("-------user message-------")
    print(user_msg)