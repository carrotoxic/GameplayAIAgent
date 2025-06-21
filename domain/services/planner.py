from domain.ports import LLMPort, ParserPort, PromptBuilderPort, ChestRepositoryPort, ObservationBuilderPort
from domain.models import Belief, Desire, Context, Intention
from domain.exceptions import PlanningError

class PlanningService:
    """
    Domain-pure planner.

    Responsibilities:
    ---------------
    • Build a prompt from (belief, desire, context).
    • Call the LLM via injected `LLMPort`.
    • Parse the reply into a domain `Intention` object.
    """

    def __init__(self, 
                 llm: LLMPort, 
                 prompt_builder: PromptBuilderPort, 
                 parser: ParserPort,
                 chest_repo: ChestRepositoryPort, 
                 obs_builder: ObservationBuilderPort):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._parser = parser
        self._chest_repo = chest_repo
        self._obs_builder = obs_builder

    def plan(self, belief: Belief, desire: Desire, context: Context) -> Intention:
        system_msg, user_msg = self._prompt_builder.build_prompt(belief, desire, context)
        llm_response = self._llm.chat([system_msg, user_msg])

        try:
            program_meta = self._parser.extract_main_function(llm_response)
        except Exception as exc:
            raise PlanningError("Failed to parse LLM reply") from exc
        
        return Intention(code=program_meta.program_code,
                         exec_snippet = program_meta.exec_code)
    
