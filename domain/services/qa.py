from domain.ports.llm_port import LLMPort
from domain.ports.prompt_builder_port import PromptBuilderPort
from domain.ports.parser_port import ParserPort
from domain.ports.database_port import DatabasePort
from domain.models.observation import Observation
from domain.models.qa_entry import QAEntry

class QAService:
    def __init__(
        self,
        llm: LLMPort,
        question_prompt_builder: PromptBuilderPort,
        answer_prompt_builder: PromptBuilderPort,
        parser: ParserPort,
        database: DatabasePort,
    ):
        self._llm = llm
        self._question_prompt_builder = question_prompt_builder
        self._answer_prompt_builder = answer_prompt_builder
        self._parser = parser
        self._database = database

    def generate_context(self, observation: Observation) -> list[QAEntry]:
        """Return 'Question / Answer' lines to insert into the prompt."""
        # step1: generate questions
        questions = self.generate_questions(observation)

        # step2: generate answers
        qa_entries = self.generate_answers(questions)

        # step3: return qa_entries
        return qa_entries

    def generate_questions(self, observation: Observation) -> list[str]:
        """Generate questions based on the observation."""
        system_msg, user_msg = self._question_prompt_builder.build_prompt(observation=observation)
        llm_response = self._llm.chat([system_msg, user_msg])
        questions = self._parser.parse(llm_response.content)

        return questions
    

    def generate_answers(self, questions: list[str]) -> list[str]:
        """Generate answers for each question."""
        qa_entries: list[QAEntry] = []
        for question in questions:
            cached = self._database.lookup(question)
            if cached:
                answer = cached
            else:
                system_msg, user_msg = self._answer_prompt_builder.build_prompt(question=question)
                llm_response = self._llm.chat([system_msg, user_msg])
                answer = llm_response.content
                self._database.store(texts=[question], metadatas=[{"question": question}])
            qa_entries.append(QAEntry(question=question, answer=answer))
        return qa_entries

if __name__ == "__main__":

    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.prompts.registry import get
    from infrastructure.adapters.database.chroma_database import ChromaDatabase
    from domain.models.event import Event
    from domain.models.task import Task
    import infrastructure.prompts.builders.qa_question_prompt_builder
    import infrastructure.prompts.builders.qa_answer_prompt_builder
    from infrastructure.prompts.builders.minecraft_observation_builder import MinecraftObservationBuilder
    from infrastructure.parsers.qa_question_parser import QAQuestionParser

    qa_service = QAService(
        llm=LangchainOllamaLLM(),
        question_prompt_builder=get("qa_question"),
        answer_prompt_builder=get("qa_answer"),
        parser=QAQuestionParser(),
        database=ChromaDatabase(collection_name="qa_cache"),
    )

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

    tasks = [
        Task(task="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
        Task(task="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    ]

    obs_builder = MinecraftObservationBuilder()
    obs = obs_builder.build(event=event, completed=tasks[:1], failed=tasks[1:])

    questions = qa_service.generate_questions(obs)
    print(questions) 
    answers = qa_service.generate_answers(questions)
    print(answers)
