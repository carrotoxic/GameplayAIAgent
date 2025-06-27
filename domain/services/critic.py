from domain.ports import LLMPort, ParserPort, PromptBuilderPort
from domain.models import Task, Observation

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

    def evaluate(self, observation: Observation, task: Task) -> tuple[bool, str]:
        system_msg, user_msg = self._prompt_builder.build_prompt(observation=observation, task=task)
        llm_response = self._llm.chat([system_msg, user_msg])
        success, critique = self._parser.parse(llm_response.content)
        return success, critique


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    from domain.models import Task, Observation
    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.prompts.registry import get
    from infrastructure.parsers import CriticParser

    task = Task(command="Mine 1 gold log", reasoning="Need gold", context="Tutorial")

    observation = Observation(
        position={"x": 10.5, "y": 64.0, "z": -5.2},
        inventory={"oak_log": 3, "wooden_pickaxe": 1},
        health=18.5,
        hunger=15.0,
        biome="forest",
        nearby_blocks=["grass", "dirt", "stone", "oak_log"],
        nearby_entities={"cow": 5.0},
        time="day",
        other_blocks="iron_ore",
        equipment={"helmet": "leather_helmet"},
        chests={"Chest 1": "iron_ingot: 8", "Chest 2": "iron_ingot: 8"},
        error_message="Evaluation error: Runtime error: Took to long to decide path to goal!",
        chat_message="Explore success.",
    )

    critic_service = CriticService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get("minecraft", "critic"),
        parser=CriticParser()
    )

    success, critique = critic_service.evaluate(observation, task)
    print(success, critique)