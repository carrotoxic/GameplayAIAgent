import pytest
from unittest.mock import Mock, MagicMock
from domain.services.qa import QAService
from domain.models import Observation, QAEntry


class TestQAService:
    """Unit tests for QAService"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM port for testing"""
        llm = Mock()
        llm.chat.return_value = "Mock LLM response"
        return llm

    @pytest.fixture
    def mock_prompt_builder(self):
        """Mock prompt builder for testing"""
        builder = Mock()
        builder.build_qa_question_prompt.return_value = ("System message", "User message")
        builder.build_qa_answer_prompt.return_value = ("System message", "User message")
        return builder

    @pytest.fixture
    def mock_cache(self):
        """Mock QA cache for testing"""
        cache = Mock()
        cache.lookup.return_value = None
        cache.store.return_value = None
        return cache

    @pytest.fixture
    def mock_parser(self):
        """Mock parser for testing"""
        parser = Mock()
        parser.parse_qa_questions.return_value = [
            "What should I do next?",
            "What tools do I need?"
        ]
        return parser

    @pytest.fixture
    def sample_observation(self):
        """Sample observation for testing"""
        return Observation(
            context="Player is in a plains biome",
            biome="plains",
            time="day",
            nearby_blocks="grass, dirt, stone",
            other_blocks="",
            nearby_entities="cow, pig",
            health="20.0/20",
            hunger="20.0/20",
            position="x=0, y=64, z=0",
            equipment="",
            inventory="wooden_pickaxe: 1, oak_log: 3",
            chests="",
            completed_tasks="Mine 1 wood log",
            failed_tasks=""
        )

    def test_qa_service_initialization(self, mock_llm, mock_prompt_builder, 
                                     mock_cache, mock_parser):
        """Test QAService initialization"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        assert service._llm == mock_llm
        assert service._prompt_builder == mock_prompt_builder
        assert service._cache == mock_cache
        assert service._parser == mock_parser

    def test_generate_context_success(self, mock_llm, mock_prompt_builder, 
                                    mock_cache, mock_parser, sample_observation):
        """Test successful context generation"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock LLM responses for answers
        mock_llm.chat.side_effect = [
            "Mock LLM response",  # For questions
            "Mine some stone",    # Answer 1
            "A pickaxe"           # Answer 2
        ]
        
        qa_entries = service.generate_context(sample_observation)
        
        # Verify all components were called correctly
        mock_prompt_builder.build_qa_question_prompt.assert_called_once_with(sample_observation)
        mock_llm.chat.assert_called()
        mock_parser.parse_qa_questions.assert_called_once_with("Mock LLM response")
        
        # Verify cache was checked for each question
        assert mock_cache.lookup.call_count == 2
        
        # Verify answers were stored in cache
        assert mock_cache.store.call_count == 2
        
        # Verify returned QA entries
        assert len(qa_entries) == 2
        assert isinstance(qa_entries[0], QAEntry)
        assert isinstance(qa_entries[1], QAEntry)
        assert qa_entries[0].question == "What should I do next?"
        assert qa_entries[0].answer == "Mine some stone"
        assert qa_entries[1].question == "What tools do I need?"
        assert qa_entries[1].answer == "A pickaxe"

    def test_generate_context_with_cached_answers(self, mock_llm, mock_prompt_builder, 
                                                mock_cache, mock_parser, sample_observation):
        """Test context generation with cached answers"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock cache to return cached answers
        mock_cache.lookup.side_effect = [
            "Cached answer 1",  # First question cached
            None                # Second question not cached
        ]
        
        # Mock LLM response for the uncached question
        mock_llm.chat.side_effect = [
            "Mock LLM response",  # For questions
            "New answer 2"        # Answer for uncached question
        ]
        
        qa_entries = service.generate_context(sample_observation)
        
        # Verify cache was checked for each question
        assert mock_cache.lookup.call_count == 2
        
        # Verify only uncached answer was stored
        assert mock_cache.store.call_count == 1
        
        # Verify returned QA entries
        assert len(qa_entries) == 2
        assert qa_entries[0].answer == "Cached answer 1"
        assert qa_entries[1].answer == "New answer 2"

    def test_generate_context_no_questions(self, mock_llm, mock_prompt_builder, 
                                         mock_cache, mock_parser, sample_observation):
        """Test context generation when no questions are generated"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock parser to return no questions
        mock_parser.parse_qa_questions.return_value = []
        
        qa_entries = service.generate_context(sample_observation)
        
        # Verify no cache operations or answer generation
        assert mock_cache.lookup.call_count == 0
        assert mock_cache.store.call_count == 0
        
        # Verify empty result
        assert len(qa_entries) == 0

    def test_generate_context_llm_error(self, mock_llm, mock_prompt_builder, 
                                      mock_cache, mock_parser, sample_observation):
        """Test handling of LLM errors during question generation"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Make LLM raise an exception
        mock_llm.chat.side_effect = Exception("LLM service down")
        
        with pytest.raises(Exception) as exc_info:
            service.generate_context(sample_observation)
        
        assert "LLM service down" in str(exc_info.value)

    def test_generate_context_parser_error(self, mock_llm, mock_prompt_builder, 
                                         mock_cache, mock_parser, sample_observation):
        """Test handling of parser errors during question parsing"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Make parser raise an exception
        mock_parser.parse_qa_questions.side_effect = Exception("Parse error")
        
        with pytest.raises(Exception) as exc_info:
            service.generate_context(sample_observation)
        
        assert "Parse error" in str(exc_info.value)

    def test_generate_context_answer_generation_error(self, mock_llm, mock_prompt_builder, 
                                                    mock_cache, mock_parser, sample_observation):
        """Test handling of errors during answer generation"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock LLM to fail on answer generation
        mock_llm.chat.side_effect = [
            "Mock LLM response",  # For questions (success)
            Exception("Answer generation failed")  # For answer (failure)
        ]
        
        with pytest.raises(Exception) as exc_info:
            service.generate_context(sample_observation)
        
        assert "Answer generation failed" in str(exc_info.value)

    def test_generate_context_cache_error(self, mock_llm, mock_prompt_builder, 
                                        mock_cache, mock_parser, sample_observation):
        """Test handling of cache errors"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock cache to raise an exception
        mock_cache.lookup.side_effect = Exception("Cache error")
        
        with pytest.raises(Exception) as exc_info:
            service.generate_context(sample_observation)
        
        assert "Cache error" in str(exc_info.value)

    def test_generate_context_multiple_questions(self, mock_llm, mock_prompt_builder, 
                                               mock_cache, mock_parser, sample_observation):
        """Test context generation with multiple questions"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock parser to return multiple questions
        mock_parser.parse_qa_questions.return_value = [
            "What should I do next?",
            "What tools do I need?",
            "Where should I go?",
            "What resources are available?"
        ]
        
        # Mock LLM responses for answers
        mock_llm.chat.side_effect = [
            "Mock LLM response",  # For questions
            "Mine some stone",    # Answer 1
            "A pickaxe",          # Answer 2
            "Go to the cave",     # Answer 3
            "Stone and wood"      # Answer 4
        ]
        
        qa_entries = service.generate_context(sample_observation)
        
        # Verify correct number of QA entries
        assert len(qa_entries) == 4
        
        # Verify all questions and answers
        expected_questions = [
            "What should I do next?",
            "What tools do I need?",
            "Where should I go?",
            "What resources are available?"
        ]
        expected_answers = [
            "Mine some stone",
            "A pickaxe",
            "Go to the cave",
            "Stone and wood"
        ]
        
        for i, entry in enumerate(qa_entries):
            assert entry.question == expected_questions[i]
            assert entry.answer == expected_answers[i]

    def test_generate_context_prompt_builder_integration(self, mock_llm, mock_prompt_builder, 
                                                        mock_cache, mock_parser, sample_observation):
        """Test integration with prompt builder"""
        service = QAService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            cache=mock_cache,
            parser=mock_parser
        )
        
        # Mock questions and answers
        questions = ["What should I do next?"]
        mock_parser.parse_qa_questions.return_value = questions
        mock_llm.chat.side_effect = ["Mock LLM response", "Mine some stone"]
        
        service.generate_context(sample_observation)
        
        # Verify prompt builder calls
        mock_prompt_builder.build_qa_question_prompt.assert_called_once_with(sample_observation)
        mock_prompt_builder.build_qa_answer_prompt.assert_called_once_with("What should I do next?") 