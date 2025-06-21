import pytest
from unittest.mock import Mock, MagicMock
from domain.services.curriculum import CurriculumService
from domain.services.qa import QAService
from domain.models import Event, Task, Observation, QAEntry
from domain.exceptions import ProposalError


class TestCurriculumService:
    """Unit tests for CurriculumService"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM port for testing"""
        llm = Mock()
        llm.chat.return_value = "Mock LLM response"
        return llm

    @pytest.fixture
    def mock_qa_service(self):
        """Mock QA service for testing"""
        qa_service = Mock(spec=QAService)
        qa_service.generate_context.return_value = [
            QAEntry(question="What should I do next?", answer="Mine some stone"),
            QAEntry(question="What tools do I need?", answer="A pickaxe")
        ]
        return qa_service

    @pytest.fixture
    def mock_prompt_builder(self):
        """Mock prompt builder for testing"""
        builder = Mock()
        builder.build.return_value = Mock(spec=Observation)
        builder.build_prompt.return_value = ("System message", "User message")
        return builder

    @pytest.fixture
    def mock_parser(self):
        """Mock parser for testing"""
        parser = Mock()
        parser.parse_reply.return_value = Task(
            task="Mine 5 stone blocks",
            reasoning="Stone is needed for crafting",
            context="Basic mining task"
        )
        return parser

    @pytest.fixture
    def sample_event(self):
        """Sample event for testing"""
        return Event(
            position={"x": 0, "y": 64, "z": 0},
            inventory={"wooden_pickaxe": 1, "oak_log": 3},
            health=20.0,
            hunger=20.0,
            biome="plains",
            nearby_blocks=["grass", "dirt", "stone"],
            nearby_entities={"cow": 5.0, "pig": 8.0},
            time="day",
            other_blocks="",
            equipment={},
            chests=""
        )

    @pytest.fixture
    def sample_task(self):
        """Sample task for testing"""
        return Task(
            task="Mine 5 stone blocks",
            reasoning="Stone is needed for crafting",
            context="Basic mining task"
        )

    def test_curriculum_service_initialization(self, mock_llm, mock_qa_service, 
                                             mock_prompt_builder, mock_parser):
        """Test CurriculumService initialization"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        assert service._llm == mock_llm
        assert service._qa == mock_qa_service
        assert service._prompt_builder == mock_prompt_builder
        assert service._parser == mock_parser
        assert service._completed == []
        assert service._failed == []

    def test_next_task_success(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                              mock_parser, sample_event):
        """Test successful task generation"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        task = service.next_task(sample_event)
        
        # Verify all components were called correctly
        mock_prompt_builder.build.assert_called_once_with(
            sample_event, [], []
        )
        mock_qa_service.generate_context.assert_called_once()
        mock_prompt_builder.build_prompt.assert_called_once()
        mock_llm.chat.assert_called_once()
        mock_parser.parse_reply.assert_called_once_with("Mock LLM response")
        
        assert isinstance(task, Task)
        assert task.task == "Mine 5 stone blocks"
        assert task.reasoning == "Stone is needed for crafting"
        assert task.context == "Basic mining task"

    def test_next_task_with_completed_and_failed_tasks(self, mock_llm, mock_qa_service, 
                                                      mock_prompt_builder, mock_parser, 
                                                      sample_event, sample_task):
        """Test task generation with existing completed and failed tasks"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Add some completed and failed tasks
        service.add_completed_task(sample_task)
        service.add_failed_task(Task(
            task="Craft diamond pickaxe",
            reasoning="Too advanced",
            context="Not enough resources"
        ))
        
        task = service.next_task(sample_event)
        
        # Verify prompt builder was called with the task lists
        mock_prompt_builder.build.assert_called_once()
        call_args = mock_prompt_builder.build.call_args
        assert call_args[0][0] == sample_event
        assert len(call_args[0][1]) == 1  # completed tasks
        assert len(call_args[0][2]) == 1  # failed tasks

    def test_next_task_parser_error(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                                   mock_parser, sample_event):
        """Test handling of parser errors"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Make parser raise an exception
        mock_parser.parse_reply.side_effect = Exception("Parse error")
        
        with pytest.raises(ProposalError) as exc_info:
            service.next_task(sample_event)
        
        assert "Failed to parse LLM reply" in str(exc_info.value)
        assert exc_info.value.__cause__ is not None

    def test_next_task_llm_error(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                                mock_parser, sample_event):
        """Test handling of LLM errors"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Make LLM raise an exception
        mock_llm.chat.side_effect = Exception("LLM service down")
        
        with pytest.raises(ProposalError) as exc_info:
            service.next_task(sample_event)
        
        assert "Failed to parse LLM reply" in str(exc_info.value)

    def test_add_completed_task(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                               mock_parser, sample_task):
        """Test adding completed tasks"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Initially empty
        assert len(service._completed) == 0
        assert len(service._failed) == 0
        
        # Add completed task
        service.add_completed_task(sample_task)
        assert len(service._completed) == 1
        assert service._completed[0] == sample_task
        assert len(service._failed) == 0

    def test_add_failed_task(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                            mock_parser, sample_task):
        """Test adding failed tasks"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Initially empty
        assert len(service._completed) == 0
        assert len(service._failed) == 0
        
        # Add failed task
        service.add_failed_task(sample_task)
        assert len(service._failed) == 1
        assert service._failed[0] == sample_task
        assert len(service._completed) == 0

    def test_task_movement_between_lists(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                                        mock_parser, sample_task):
        """Test moving tasks between completed and failed lists"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Add to completed first
        service.add_completed_task(sample_task)
        assert len(service._completed) == 1
        assert len(service._failed) == 0
        
        # Move to failed (should remove from completed)
        service.add_failed_task(sample_task)
        assert len(service._completed) == 0
        assert len(service._failed) == 1
        
        # Move back to completed (should remove from failed)
        service.add_completed_task(sample_task)
        assert len(service._completed) == 1
        assert len(service._failed) == 0

    def test_multiple_tasks_management(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                                     mock_parser):
        """Test managing multiple tasks"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        task1 = Task(task="Mine stone", reasoning="Need stone", context="Basic task")
        task2 = Task(task="Craft pickaxe", reasoning="Need tool", context="Crafting")
        task3 = Task(task="Build house", reasoning="Need shelter", context="Building")
        
        # Add multiple tasks
        service.add_completed_task(task1)
        service.add_completed_task(task2)
        service.add_failed_task(task3)
        
        assert len(service._completed) == 2
        assert len(service._failed) == 1
        assert task1 in service._completed
        assert task2 in service._completed
        assert task3 in service._failed

    def test_qa_service_integration(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                                   mock_parser, sample_event):
        """Test integration with QA service"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Mock QA entries
        qa_entries = [
            QAEntry(question="What should I do next?", answer="Mine some stone"),
            QAEntry(question="What tools do I need?", answer="A pickaxe")
        ]
        mock_qa_service.generate_context.return_value = qa_entries
        
        service.next_task(sample_event)
        
        # Verify QA service was called with the observation
        mock_qa_service.generate_context.assert_called_once()
        call_args = mock_qa_service.generate_context.call_args
        assert isinstance(call_args[0][0], Observation)

    def test_prompt_builder_integration(self, mock_llm, mock_qa_service, mock_prompt_builder, 
                                       mock_parser, sample_event):
        """Test integration with prompt builder"""
        service = CurriculumService(
            llm=mock_llm,
            qa_service=mock_qa_service,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Mock observation and QA entries
        mock_observation = Mock(spec=Observation)
        mock_prompt_builder.build.return_value = mock_observation
        
        qa_entries = [QAEntry(question="Test?", answer="Test answer")]
        mock_qa_service.generate_context.return_value = qa_entries
        
        service.next_task(sample_event)
        
        # Verify prompt builder calls
        mock_prompt_builder.build.assert_called_once()
        mock_prompt_builder.build_prompt.assert_called_once_with(qa_entries, mock_observation) 