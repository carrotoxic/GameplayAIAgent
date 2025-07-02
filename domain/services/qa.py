from typing import List, Optional, Sequence
from ..ports import LLMPort, DatabasePort, PromptBuilderPort
from ..models import Task, Observation, Message
from ..ports.parser_port import ParserPort

class QAService:
    """
    Service for question answering.
    """
    def __init__(self,
                 llm: LLMPort,
                 question_prompt_builder: PromptBuilderPort,
                 answer_prompt_builder: PromptBuilderPort,
                 parser: ParserPort,
                 database: DatabasePort,
                 resume: bool = False
                 ):
        self._llm = llm
        self._question_prompt_builder = question_prompt_builder
        self._answer_prompt_builder = answer_prompt_builder
        self._parser = parser
        self._database = database
        self.question_answer_pairs: List[tuple[str, str]] = []

        if resume and self._database:
            # self.question_answer_pairs = self._database.load()
            pass

    def get_question_answer_pairs(self, top_k: int) -> List[tuple[str, str]]:
        return self.question_answer_pairs[-top_k:]

    async def get_questions(self, observation: Observation, completed_tasks: List[Task], failed_tasks: List[Task]) -> Sequence[str]:
        # Caching logic removed for now as it was based on a simple string context.
        # A more sophisticated caching strategy would be needed for observation/task objects.

        # Generate new questions
        system_msg, user_msg = self._question_prompt_builder.build_prompt(
            observation=observation,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
        )
        response = await self._llm.chat([system_msg, user_msg])
        questions = self._parser.parse(response.content)
        
        # Add the new questions to the database for future use if needed,
        # but the query mechanism would need to be more advanced.
        # await self._database.add(questions) 
        return questions

    async def get_answer(self, question: str) -> str:
        system_msg, user_msg = self._answer_prompt_builder.build_prompt(question=question)
        response = await self._llm.chat([system_msg, user_msg])
        return response.content

    async def generate_qa(self, observation: Observation, task: Task) -> List[tuple[str, str]]:
        system_msg, user_msg = self._question_prompt_builder.build_prompt(
            observation=observation,
            task=task,
        )
        llm_response = await self._llm.chat([system_msg, user_msg])
        questions = self._parser.parse(llm_response).content

        for question in questions:
            system_msg, user_msg = self._answer_prompt_builder.build_prompt(
                question=question,
                observation=observation,
            )
            answer = await self._llm.chat([system_msg, user_msg])
            self.question_answer_pairs.append((question, answer.content))
            
        return self.question_answer_pairs

if __name__ == "__main__":

    from infrastructure.adapters.llm.ollama_llm import LangchainOllamaLLM
    from infrastructure.prompts.registry import get
    from infrastructure.adapters.database.chroma_database import ChromaDatabase
    from domain.models import Event, Task
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder
    from infrastructure.parsers.qa_question_parser import QAQuestionParser

    qa_service = QAService(
        llm=LangchainOllamaLLM(),
        question_prompt_builder=get(game="minecraft", name="qa_question"),
        answer_prompt_builder=get(game="minecraft", name="qa_answer"),
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
        chests={"Chest 1": "iron_ingot: 8", "Chest 2": "iron_ingot: 8"},
    )

    tasks = [
        Task(command="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
        Task(command="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    ]

    obs_builder = MinecraftObservationBuilder()
    obs = obs_builder.build(event=event)    

    qa_text = qa_service.generate_context(obs, tasks[:1], tasks[1:])
    print(qa_text)
