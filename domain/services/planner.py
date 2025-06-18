'''
planner is a domain service that is used to plan the actions of the agent.
It should not depend on any other external services.

'''


class PlanningService:
    """
    Domain-pure planner: converts Belief + Desire (+ Context) into Intention.
    """

    def __init__(self, 
                 llm: LLMPort, 
                 parser: ParserPort,
                 chest_repo: ChestRepositoryPort, 
                 obs_builder: ObservationBuilderPort):

    def plan(self, belief: Belief, desire: Desire, context: Context) -> Intention:
        sys_msg, user_msg = self._build_prompt(belief, desire, context)
        llm_response = self.llm.chat([sys_msg, user_msg])

        try:
            program_meta = self._parser.extract_main_function(llm_response)
        except Exception as exc:
            raise PlanningError("Failed to parse LLM reply") from exc
        
        return Intention(code=program_meta.program_code,
                         exec_snnipet = program_meta.exec_code)
    
    