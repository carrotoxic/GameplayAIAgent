import pytest
from unittest.mock import Mock, MagicMock
from domain.models import Event, ChestSnapshot, TaskProposal, Belief, Desire, Context, Intention, Critique
from domain.ports import LLMPort, PromptBuilderPort, QACachePort, ParserPort, ChestRepositoryPort, ObservationBuilderPort


@pytest.fixture
def mock_llm():
    """Mock LLM port for testing"""
    llm = Mock(spec=LLMPort)
    llm.chat.return_value = "Mock LLM response"
    return llm


@pytest.fixture
def mock_qa_llm():
    """Mock QA LLM port for testing"""
    qa_llm = Mock(spec=LLMPort)
    qa_llm.chat.return_value = "Mock QA LLM response"
    return qa_llm


@pytest.fixture
def mock_prompt_builder():
    """Mock prompt builder for testing"""
    builder = Mock(spec=PromptBuilderPort)
    builder.build_prompt.return_value = ("System message", "User message")
    return builder


@pytest.fixture
def mock_qa_prompt_builder():
    """Mock QA prompt builder for testing"""
    builder = Mock(spec=PromptBuilderPort)
    builder.build_prompt.return_value = ("QA System message", "QA User message")
    return builder


@pytest.fixture
def mock_parser():
    """Mock parser for testing"""
    parser = Mock(spec=ParserPort)
    parser.parse_reply.return_value = Mock(task="Test task", context="Test context")
    parser.extract_critique.return_value = Mock(success=True, critique="Good job!")
    parser.extract_main_function.return_value = Mock(program_code="test()", exec_code="await test()")
    return parser


@pytest.fixture
def mock_qa_cache():
    """Mock QA cache for testing"""
    cache = Mock(spec=QACachePort)
    cache.get.return_value = None
    cache.set.return_value = None
    return cache


@pytest.fixture
def mock_chest_repo():
    """Mock chest repository for testing"""
    repo = Mock(spec=ChestRepositoryPort)
    repo.get_chests.return_value = []
    return repo


@pytest.fixture
def mock_obs_builder():
    """Mock observation builder for testing"""
    builder = Mock(spec=ObservationBuilderPort)
    builder.build_observation.return_value = "Mock observation"
    return builder


@pytest.fixture
def sample_event():
    """Sample event for testing"""
    return Event(
        position={"x": 0, "y": 64, "z": 0},
        inventory={"wooden_pickaxe": 1, "oak_log": 3},
        health=20.0,
        hunger=20.0,
        biome="plains",
        nearby_blocks=["grass", "dirt", "stone"],
        nearby_entities={"cow": 5.0, "pig": 8.0}
    )


@pytest.fixture
def sample_task_proposal():
    """Sample task proposal for testing"""
    return TaskProposal(
        task="Mine 5 stone blocks",
        context="You need stone to craft better tools"
    )


@pytest.fixture
def sample_belief():
    """Sample belief for testing"""
    return Belief(
        position={"x": 0, "y": 64, "z": 0},
        inventory={"wooden_pickaxe": 1},
        health=20.0,
        biome="plains"
    )


@pytest.fixture
def sample_desire():
    """Sample desire for testing"""
    return Desire(
        goal="Craft a stone pickaxe",
        priority=1.0
    )


@pytest.fixture
def sample_context():
    """Sample context for testing"""
    return Context(
        completed_tasks=["Mine 1 wood log"],
        failed_tasks=[],
        current_time="day"
    )


@pytest.fixture
def sample_intention():
    """Sample intention for testing"""
    return Intention(
        code="async function mineStone() { await mineBlock(bot, 'stone', 5); }",
        exec_snippet="await mineStone();"
    )


@pytest.fixture
def sample_critique():
    """Sample critique for testing"""
    return Critique(
        success=True,
        critique="Successfully mined the required blocks"
    )


@pytest.fixture
def warmup_thresholds():
    """Sample warmup thresholds for testing"""
    return Mock(
        context=15,
        biome=10,
        time=15,
        nearby_blocks=0,
        other_blocks=10,
        nearby_entities=5,
        health=15,
        hunger=15,
        position=0,
        equipment=0,
        inventory=0,
        optional_inventory_items=7,
        chests=0,
        completed_tasks=0,
        failed_tasks=0
    )
