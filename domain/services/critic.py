from domain.ports import LLMPort, ParserPort, PromptBuilderPort
from domain.models import Event, Context, Intention, Critique

class CriticService:
    """
    Domain-pure Critic.

    Responsibilities
    ---------------
    • Build a critique prompt from (intention, result, context).  
    • Call the LLM via injected `LLMPort`.  
    • Parse the reply into a domain `Critique` object.  
    """

    def __init__(
        self,
        llm: LLMPort,
        prompt_builder: PromptBuilderPort,
        parser: ParserPort
    ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._parser = parser

    def evaluate(self, intention: Intention, result: Event, context: Context) -> Critique:
        system_msg, user_msg = self._prompt_builder.build_prompt(intention, result, context)
        llm_response = self._llm.chat([system_msg, user_msg])
        try:
            critique_meta = self._parser.extract_critique(llm_response)
            assert critique_meta.success in [True, False]
        except Exception as exc:
            raise CriticError("Failed to parse LLM reply") from exc
        return Critique(success=critique_meta.success,
                        critique=critique_meta.critique)
                        