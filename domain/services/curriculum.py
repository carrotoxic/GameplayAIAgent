from domain.ports.llm_port import LLMPort
from domain.ports.prompt_builder_port import PromptBuilderPort
from domain.ports.parser_port import ParserPort
from domain.services.qa import QAService
from domain.models import Task, Observation
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
        prompt_builder: PromptBuilderPort,
        parser: ParserPort,
        # TODO: add warmup thresholds
        # warmup_thresholds: WarmupThresholds,
    ):
        self._llm = llm
        self._qa = qa_service
        self._prompt_builder = prompt_builder
        self._parser = parser
        # self._warmup = warmup_thresholds
        self._completed_tasks: List[Task] = []
        self._failed_tasks: List[Task] = []

    def next_task(
        self, observation: Observation) -> Task:
        """
        Decide the next Task. May raise ProposalFailed when the LLM
        reply cannot be parsed after several retries.
        """

        # generate game related question and answer as context
        qa_text = self._qa.generate_context(observation, self._completed_tasks, self._failed_tasks)

        # build final prompt and send to LLM
        system_msg, user_msg = self._prompt_builder.build_prompt(
            qa_text=qa_text,
            observation=observation,
            completed_tasks=self._completed_tasks,
            failed_tasks=self._failed_tasks,
        )
        llm_response = self._llm.chat([system_msg, user_msg])
        try:
            # parse LLM response to task proposal model
            task = self._parser.parse(llm_response.content)
            task.context = qa_text
            return task
        except Exception as exc:
            raise Exception("Failed to parse LLM reply") from exc

    # store result of previous task
    def add_completed_task(self, task: Task) -> None:
        self._completed_tasks.append(task)
        if task in self._failed_tasks:
            self._failed_tasks.remove(task)

    def add_failed_task(self, task: Task) -> None:
        self._failed_tasks.append(task)
        if task in self._completed_tasks:
            self._completed_tasks.remove(task)

    def get_completed_tasks(self) -> List[Task]:
        return self._completed_tasks
    
    def get_failed_tasks(self) -> List[Task]:
        return self._failed_tasks


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":

    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.adapters.database.chroma_database import ChromaDatabase
    from infrastructure.prompts.registry import get
    from infrastructure.parsers.task_parser import TaskParser
    from infrastructure.parsers.qa_question_parser import QAQuestionParser
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder


    
    qa_service = QAService(
        llm=LangchainOllamaLLM(),
        question_prompt_builder=get(game="minecraft", name="qa_question"),
        answer_prompt_builder=get(game="minecraft", name="qa_answer"),
        parser=QAQuestionParser(),
        database=ChromaDatabase(collection_name="qa_cache"),
    )

    observation_builder = MinecraftObservationBuilder()

    curriculum_service = CurriculumService(
        llm=LangchainOllamaLLM(),
        qa_service=qa_service,
        observation_builder=observation_builder,
        curriculum_prompt_builder=get(game="minecraft", name="curriculum"),
        parser=TaskParser(),
    )

    # task = curriculum_service.next_task(observation)
    # print(task)