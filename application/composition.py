# application/bootstrap.py

from domain.services import CurriculumService, QAService, CriticService, PlannerService, SkillService
from application.agent_controller import AgentController
from infrastructure.adapters.llm import LangchainOllamaLLM
from infrastructure.adapters.database import ChromaDatabase
from infrastructure.adapters.game.minecraft import MinecraftObservationBuilder, MineflayerEnvironment, MineflayerProcessManager, MineflayerAPIClient
from infrastructure.parsers import  QAQuestionParser, TaskParser, JSParser, CriticParser
from infrastructure.prompts.registry import get
from pathlib import Path
import logging

def build_agent(game: str) -> AgentController:
    # LLM
    llm = LangchainOllamaLLM()

    # QA Service
    qa_service = QAService(
        llm=llm,
        question_prompt_builder=get(game=game, name="qa_question"),
        answer_prompt_builder=get(game=game, name="qa_answer"),
        parser=QAQuestionParser(),
        database=ChromaDatabase(collection_name="qa_cache")
    )

    # Curriculum Service
    curriculum_service = CurriculumService(
        llm=llm,
        qa_service=qa_service,
        prompt_builder=get(game=game, name="curriculum"),
        parser=TaskParser()
    )

    # planner service
    planner_service = PlannerService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get(game=game, name="planner"),
        parser=JSParser(),
    )

    # critic service
    critic_service = CriticService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get(game=game, name="critic"),
        parser=CriticParser(),
    )

    # skill service
    skill_service = SkillService(
        llm=LangchainOllamaLLM(),
        prompt_builder=get(game=game, name="skill_description"),
        database=ChromaDatabase(collection_name="skill_library"),
    )

    # Game Environment adapter
    script_path = Path(__file__).parent.parent / Path("infrastructure/adapters/game/minecraft/mineflayer_server/index.js")
    env = MineflayerEnvironment(
        api_client=MineflayerAPIClient(host="localhost", port=3000, timeout=600),
        process_manager=MineflayerProcessManager(
            script_path=script_path,
            logger=logging.getLogger(__name__)
        ),
        observation_builder=MinecraftObservationBuilder()
    )

    # Return controller with all dependencies injected
    agent_controller = AgentController(
        curriculum_service=curriculum_service,
        skill_service=skill_service,
        planner_service=planner_service,
        critic_service=critic_service,
        env=env,
        primitive_skill_dir="infrastructure/primitive_skill"
    )

    return agent_controller