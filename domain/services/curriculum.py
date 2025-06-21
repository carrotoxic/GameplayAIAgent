from domain.ports.llm_port import LLMPort
from domain.ports.prompt_builder_port import PromptBuilderPort
from domain.ports.parser_port import ParserPort
from domain.services.qa import QAService
from domain.models import Task, Event, Observation
from typing import List

class CurriculumService:
    """
    Domain-pure curriculum.

    Responsibilities:
    ---------------
    • Build a proposal prompt from (observation, chests).
    • Call the LLM via injected `LLMPort`.
    • Parse the reply into a domain `Task` object.
    ---------------
    """

    def __init__(
        self,
        llm: LLMPort,
        qa_service: QAService,
        observation_builder: PromptBuilderPort,
        curriculum_prompt_builder: PromptBuilderPort,
        parser: ParserPort,
        # TODO: add warmup thresholds
        # warmup_thresholds: WarmupThresholds,
    ):
        self._llm = llm
        self._qa = qa_service
        self._observation_builder = observation_builder
        self._curriculum_prompt_builder = curriculum_prompt_builder
        self._parser = parser
        # self._warmup = warmup_thresholds
        self._completed: List[Task] = []
        self._failed: List[Task] = []

    def next_task(
        self, event: Event) -> Task:
        """
        Decide the next Task. May raise ProposalFailed when the LLM
        reply cannot be parsed after several retries.
        """

        # convert raw event to observation
        observation: Observation = self._observation_builder.build(
            event=event,
            completed=self._completed,
            failed=self._failed,
        )

        # generate game related question and answer as context
        qa_entries = self._qa.generate_context(observation)
        
        # build final prompt and send to LLM
        system_msg, user_msg = self._curriculum_prompt_builder.build_prompt(
            qa_entries=qa_entries,
            observation=observation,
        )
        llm_response = self._llm.chat([system_msg, user_msg])
        try:
            # parse LLM response to task proposal model
            task = self._parser.parse(llm_response)
            task.context = qa_entries
            return task
        except Exception as exc:
            raise Exception("Failed to parse LLM reply") from exc

    # store result of previous task
    def add_completed_task(self, task: Task) -> None:
        self._completed.append(task)
        if task in self._failed:
            self._failed.remove(task)

    def add_failed_task(self, task: Task) -> None:
        self._failed.append(task)
        if task in self._completed:
            self._completed.remove(task)


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":

    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.adapters.database.chroma_database import ChromaQACache
    from infrastructure.prompts.registry import get
    from infrastructure.parsers.task_parser import TaskParser
    from infrastructure.parsers.qa_question_parser import QAQuestionParser
    from infrastructure.prompts.builders.minecraft_observation_builder import MinecraftObservationBuilder
    import infrastructure.prompts.builders.qa_question_prompt_builder
    import infrastructure.prompts.builders.qa_answer_prompt_builder
    import infrastructure.prompts.builders.curriculum_prompt_builder

    event = Event(
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
        chests="Chest 1: iron_ingot: 8",
    )
    
    qa_service = QAService(
        llm=LangchainOllamaLLM(),
        question_prompt_builder=get("qa_question"),
        answer_prompt_builder=get("qa_answer"),
        parser=QAQuestionParser(),
        cache=ChromaQACache(),
    )

    observation_builder = MinecraftObservationBuilder()

    curriculum_service = CurriculumService(
        llm=LangchainOllamaLLM(),
        qa_service=qa_service,
        observation_builder=observation_builder,
        curriculum_prompt_builder=get("curriculum"),
        parser=TaskParser(),
    )

    task = curriculum_service.next_task(event)
    print(task)