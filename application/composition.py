# application/bootstrap.py

from domain.services import CurriculumService, QAService, CriticService, PlannerService, SkillService
from application.agent_controller import AgentController
from infrastructure.adapters.llm import LangchainOllamaLLM
from infrastructure.adapters.database import ChromaDatabase
from infrastructure.adapters.game import MinecraftObservationBuilder
from infrastructure.parsers import  QAQuestionParser, TaskParser, JSParser, CriticParser
from infrastructure.prompts.registry import get


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
        observation_builder=MinecraftObservationBuilder(),
        curriculum_prompt_builder=get(game=game, name="curriculum"),
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

    # Env adapter
    # env = MinecraftEnvironmentAdapter(mc_port=25565)  # Example port

    # Return controller with all dependencies injected
    agent_controller = AgentController(
        curriculum_service=curriculum_service,
        skill_service=skill_service,
        planner_service=planner_service,
        critic_service=critic_service,
        # env=env,
        primitive_skill_dir="infrastructure/primitive_skill"
    )

    return agent_controller
