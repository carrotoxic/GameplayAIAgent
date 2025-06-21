import pytest
from unittest.mock import Mock
from domain.services.planner import PlanningService
from domain.models import Belief, Desire, Context, Intention
from domain.exceptions import PlanningError


class TestPlanningService:
    """Test cases for PlanningService"""

    def test_init(self, mock_llm, mock_prompt_builder, mock_parser, 
                  mock_chest_repo, mock_obs_builder):
        """Test PlanningService initialization"""
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        assert service._llm == mock_llm
        assert service._prompt_builder == mock_prompt_builder
        assert service._parser == mock_parser
        assert service._chest_repo == mock_chest_repo
        assert service._obs_builder == mock_obs_builder

    def test_plan_success(self, mock_llm, mock_prompt_builder, mock_parser,
                         mock_chest_repo, mock_obs_builder,
                         sample_belief, sample_desire, sample_context):
        """Test successful planning"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.extract_main_function.return_value = Mock(
            program_code="async function mineStone() { await mineBlock(bot, 'stone', 5); }",
            exec_code="await mineStone();"
        )
        
        # Execute
        result = service.plan(sample_belief, sample_desire, sample_context)
        
        # Assert
        assert isinstance(result, Intention)
        assert result.code == "async function mineStone() { await mineBlock(bot, 'stone', 5); }"
        assert result.exec_snippet == "await mineStone();"
        mock_prompt_builder.build_prompt.assert_called_once_with(
            sample_belief, sample_desire, sample_context
        )
        mock_llm.chat.assert_called_once()
        mock_parser.extract_main_function.assert_called_once_with("Mock LLM response")

    def test_plan_parser_error(self, mock_llm, mock_prompt_builder, mock_parser,
                              mock_chest_repo, mock_obs_builder,
                              sample_belief, sample_desire, sample_context):
        """Test planning when parser fails"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        mock_parser.extract_main_function.side_effect = Exception("Parse error")
        
        # Execute & Assert
        with pytest.raises(PlanningError, match="Failed to parse LLM reply"):
            service.plan(sample_belief, sample_desire, sample_context)

    def test_plan_llm_error(self, mock_llm, mock_prompt_builder, mock_parser,
                           mock_chest_repo, mock_obs_builder,
                           sample_belief, sample_desire, sample_context):
        """Test handling of LLM errors"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        mock_llm.chat.side_effect = Exception("LLM error")
        
        # Execute & Assert
        with pytest.raises(PlanningError, match="Failed to parse LLM reply"):
            service.plan(sample_belief, sample_desire, sample_context)

    def test_plan_with_empty_code(self, mock_llm, mock_prompt_builder, mock_parser,
                                 mock_chest_repo, mock_obs_builder,
                                 sample_belief, sample_desire, sample_context):
        """Test planning with empty program code"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.extract_main_function.return_value = Mock(
            program_code="",
            exec_code=""
        )
        
        # Execute
        result = service.plan(sample_belief, sample_desire, sample_context)
        
        # Assert
        assert isinstance(result, Intention)
        assert result.code == ""
        assert result.exec_snippet == ""

    def test_plan_with_complex_code(self, mock_llm, mock_prompt_builder, mock_parser,
                                   mock_chest_repo, mock_obs_builder,
                                   sample_belief, sample_desire, sample_context):
        """Test planning with complex program code"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        complex_code = """
        async function complexMining() {
            const stoneBlocks = await findBlocks(bot, 'stone', 10);
            for (const block of stoneBlocks) {
                await mineBlock(bot, block);
                await bot.pathfinder.goto(block.position);
            }
        }
        """
        exec_code = "await complexMining();"
        
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.extract_main_function.return_value = Mock(
            program_code=complex_code,
            exec_code=exec_code
        )
        
        # Execute
        result = service.plan(sample_belief, sample_desire, sample_context)
        
        # Assert
        assert isinstance(result, Intention)
        assert result.code == complex_code
        assert result.exec_snippet == exec_code

    def test_plan_with_none_context(self, mock_llm, mock_prompt_builder, mock_parser,
                                   mock_chest_repo, mock_obs_builder,
                                   sample_belief, sample_desire):
        """Test planning with None context"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.extract_main_function.return_value = Mock(
            program_code="async function simpleTask() { }",
            exec_code="await simpleTask();"
        )
        
        # Execute
        result = service.plan(sample_belief, sample_desire, None)
        
        # Assert
        assert isinstance(result, Intention)
        mock_prompt_builder.build_prompt.assert_called_once_with(
            sample_belief, sample_desire, None
        )

    def test_plan_with_high_priority_desire(self, mock_llm, mock_prompt_builder, mock_parser,
                                           mock_chest_repo, mock_obs_builder,
                                           sample_belief, sample_context):
        """Test planning with high priority desire"""
        # Setup
        service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        high_priority_desire = Desire(
            goal="Emergency: Find food immediately",
            priority=10.0
        )
        
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.extract_main_function.return_value = Mock(
            program_code="async function findFood() { await findAndEatFood(bot); }",
            exec_code="await findFood();"
        )
        
        # Execute
        result = service.plan(sample_belief, high_priority_desire, sample_context)
        
        # Assert
        assert isinstance(result, Intention)
        assert "findFood" in result.code
        mock_prompt_builder.build_prompt.assert_called_once_with(
            sample_belief, high_priority_desire, sample_context
        ) 