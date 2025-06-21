import unittest
from unittest.mock import Mock, MagicMock
from domain.services.curriculum import CurriculumService
from domain.services.qa import QAService
from domain.models import Event, Task, Observation, QAEntry


class TestCurriculumService(unittest.TestCase):
    """Simple unit tests for CurriculumService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_qa_service = Mock(spec=QAService)
        self.mock_observation_builder = Mock()
        self.mock_curriculum_prompt_builder = Mock()
        self.mock_parser = Mock()
        
        self.service = CurriculumService(
            llm=self.mock_llm,
            qa_service=self.mock_qa_service,
            observation_builder=self.mock_observation_builder,
            curriculum_prompt_builder=self.mock_curriculum_prompt_builder,
            parser=self.mock_parser
        )

    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.service._completed, [])
        self.assertEqual(self.service._failed, [])
        self.assertEqual(self.service._llm, self.mock_llm)
        self.assertEqual(self.service._qa, self.mock_qa_service)

    def test_next_task_success(self):
        """Test successful task generation"""
        # Setup mocks
        event = Event(
            position={"x": 0, "y": 64, "z": 0},
            inventory={"wooden_pickaxe": 1},
            health=20.0,
            hunger=20.0,
            biome="plains",
            nearby_blocks=["grass", "dirt"],
            nearby_entities={},
            time="day",
            other_blocks="",
            equipment={},
            chests=""
        )
        
        mock_observation = Mock(spec=Observation)
        mock_qa_entries = [QAEntry(question="What next?", answer="Mine stone")]
        mock_task = Task(task="Mine 5 stone", reasoning="Need stone", context="")
        
        self.mock_observation_builder.build.return_value = mock_observation
        self.mock_qa_service.generate_context.return_value = mock_qa_entries
        self.mock_curriculum_prompt_builder.build_prompt.return_value = ("system", "user")
        self.mock_llm.chat.return_value = "LLM response"
        self.mock_parser.parse.return_value = mock_task
        
        # Execute
        result = self.service.next_task(event)
        
        # Verify
        self.assertEqual(result, mock_task)
        self.assertEqual(result.context, mock_qa_entries)
        self.mock_observation_builder.build.assert_called_once()
        self.mock_qa_service.generate_context.assert_called_once_with(mock_observation)
        self.mock_llm.chat.assert_called_once_with(["system", "user"])

    def test_add_completed_task(self):
        """Test adding completed task"""
        task = Task(task="Test task", reasoning="Test", context="")
        
        self.service.add_completed_task(task)
        
        self.assertIn(task, self.service._completed)
        self.assertEqual(len(self.service._completed), 1)

    def test_add_failed_task(self):
        """Test adding failed task"""
        task = Task(task="Test task", reasoning="Test", context="")
        
        self.service.add_failed_task(task)
        
        self.assertIn(task, self.service._failed)
        self.assertEqual(len(self.service._failed), 1)

    def test_move_task_from_failed_to_completed(self):
        """Test moving task from failed to completed list"""
        task = Task(task="Test task", reasoning="Test", context="")
        
        # Add to failed first
        self.service.add_failed_task(task)
        self.assertIn(task, self.service._failed)
        
        # Then add to completed
        self.service.add_completed_task(task)
        self.assertIn(task, self.service._completed)
        self.assertNotIn(task, self.service._failed)


if __name__ == '__main__':
    unittest.main() 