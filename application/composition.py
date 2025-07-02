# application/bootstrap.py

from domain.services import CurriculumService, QAService, CriticService, PlannerService, SkillService
from application.agent_controller import AgentController
from infrastructure.adapters.llm import LangchainOllamaLLM, GeminiLLM
from infrastructure.adapters.database import ChromaDatabase
from infrastructure.adapters.game.minecraft import MinecraftObservationBuilder, MineflayerEnvironment, MineflayerProcessManager, MineflayerAPIClient
from infrastructure.parsers import  QAQuestionParser, TaskParser, JSParser, CriticParser
from infrastructure.prompts.registry import get
from pathlib import Path
import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def build_agent(game: str) -> AgentController:
    logging.info("--- Starting to build agent ---")

    # Choose your LLM
    logging.info("Initializing LLM...")
    llm = GeminiLLM()
    logging.info("LLM initialized.")

    logging.info("Initializing Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
    logging.info("Embeddings initialized.")

    # QA Service
    logging.info("Initializing ChromaDatabase for QA...")
    qa_db = ChromaDatabase(collection_name="qa_cache", embedding_model=embeddings)
    logging.info("ChromaDatabase for QA initialized.")
    
    logging.info("Initializing QA Service...")
    qa_service = QAService(
        llm=llm,
        question_prompt_builder=get(game=game, name="qa_question"),
        answer_prompt_builder=get(game=game, name="qa_answer"),
        parser=QAQuestionParser(),
        database=qa_db
    )
    logging.info("QA Service initialized.")

    # Curriculum Service
    logging.info("Initializing Curriculum Service...")
    curriculum_service = CurriculumService(
        llm=llm,
        qa_service=qa_service,
        prompt_builder=get(game=game, name="curriculum"),
        parser=TaskParser()
    )
    logging.info("Curriculum Service initialized.")

    # planner service
    logging.info("Initializing Planner Service...")
    planner_service = PlannerService(
        llm=llm,
        prompt_builder=get(game=game, name="planner"),
        parser=JSParser(),
    )
    logging.info("Planner Service initialized.")

    # critic service
    logging.info("Initializing Critic Service...")
    critic_service = CriticService(
        llm=llm,
        prompt_builder=get(game=game, name="critic"),
        parser=CriticParser(),
    )
    logging.info("Critic Service initialized.")

    # skill service
    logging.info("Initializing ChromaDatabase for SkillService...")
    skill_db = ChromaDatabase(collection_name="skill_library", embedding_model=embeddings, score_threshold=0.6)
    logging.info("ChromaDatabase for SkillService initialized.")
    
    logging.info("Initializing Skill Service...")
    skill_service = SkillService(
        llm=llm,
        prompt_builder=get(game=game, name="skill_description"),
        database=skill_db,
    )
    logging.info("Skill Service initialized.")

    # Game Environment adapter
    logging.info("Initializing Game Environment...")
    script_path = Path(__file__).parent.parent / Path("infrastructure/adapters/game/minecraft/mineflayer_server/index.js")
    env = MineflayerEnvironment(
        api_client=MineflayerAPIClient(host="localhost", port=3000, timeout=10*60),
        process_manager=MineflayerProcessManager(
            script_path=script_path,
            logger=logging.getLogger(__name__)
        ),
        observation_builder=MinecraftObservationBuilder()
    )
    logging.info("Game Environment initialized.")

    # Return controller with all dependencies injected
    logging.info("Initializing AgentController...")
    agent_controller = AgentController(
        curriculum_service=curriculum_service,
        skill_service=skill_service,
        planner_service=planner_service,
        critic_service=critic_service,
        env=env,
        primitive_skill_dir="infrastructure/primitive_skill"
    )
    logging.info("AgentController initialized.")
    logging.info("--- Agent build complete ---")

    return agent_controller