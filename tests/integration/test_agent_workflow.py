import pytest
from unittest.mock import Mock, patch
from domain.services.curriculum import CurriculumService
from domain.services.planner import PlanningService
from domain.services.critic import CriticService
from domain.models import Event, TaskProposal, Belief, Desire, Context, Intention, Critique
from domain.exceptions import PlanningError, ProposalError, CriticError


class TestAgentWorkflow:
    """Integration tests for the complete agent workflow"""

    def test_complete_task_execution_cycle(self, mock_llm, mock_qa_llm, mock_prompt_builder,
                                          mock_qa_prompt_builder, mock_parser, mock_qa_cache,
                                          mock_chest_repo, mock_obs_builder, warmup_thresholds,
                                          sample_event, sample_belief, sample_desire, sample_context):
        """Test the complete cycle: curriculum -> planning -> execution -> critique"""
        
        # Setup Curriculum Service
        curriculum_service = CurriculumService(
            llm=mock_llm,
            qa_llm=mock_qa_llm,
            proposal_prompt_builder=mock_prompt_builder,
            qa_prompt_builder=mock_qa_prompt_builder,
            qa_cache=mock_qa_cache,
            warmup_thresholds=warmup_thresholds
        )
        curriculum_service._parser = mock_parser
        
        # Setup Planning Service
        planning_service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        # Setup Critic Service
        critic_service = CriticService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Mock responses
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.parse_reply.return_value = Mock(
            task="Mine 5 stone blocks",
            context="You need stone to craft better tools"
        )
        mock_parser.extract_main_function.return_value = Mock(
            program_code="async function mineStone() { await mineBlock(bot, 'stone', 5); }",
            exec_code="await mineStone();"
        )
        mock_parser.extract_critique.return_value = Mock(
            success=True,
            critique="Successfully mined the required stone blocks"
        )
        
        # Step 1: Curriculum proposes next task
        task_proposal = curriculum_service.next_task(sample_event, mock_chest_repo)
        assert isinstance(task_proposal, TaskProposal)
        assert task_proposal.task == "Mine 5 stone blocks"
        
        # Step 2: Planning creates intention
        intention = planning_service.plan(sample_belief, sample_desire, sample_context)
        assert isinstance(intention, Intention)
        assert "mineStone" in intention.code
        
        # Step 3: Simulate execution result (successful)
        execution_result = Event(
            position={"x": 5, "y": 64, "z": 10},
            inventory={"stone": 5, "wooden_pickaxe": 1},
            health=20.0,
            hunger=18.0,
            biome="plains",
            nearby_blocks=["grass", "dirt"],
            nearby_entities={}
        )
        
        # Step 4: Critic evaluates the result
        critique = critic_service.evaluate(intention, execution_result, sample_context)
        assert isinstance(critique, Critique)
        assert critique.success is True
        
        # Step 5: Update curriculum progress
        curriculum_service.update_progress(task_proposal, success=True)
        assert task_proposal.task in curriculum_service._completed

    def test_task_execution_failure_cycle(self, mock_llm, mock_qa_llm, mock_prompt_builder,
                                         mock_qa_prompt_builder, mock_parser, mock_qa_cache,
                                         mock_chest_repo, mock_obs_builder, warmup_thresholds,
                                         sample_event, sample_belief, sample_desire, sample_context):
        """Test the workflow when task execution fails"""
        
        # Setup services
        curriculum_service = CurriculumService(
            llm=mock_llm,
            qa_llm=mock_qa_llm,
            proposal_prompt_builder=mock_prompt_builder,
            qa_prompt_builder=mock_qa_prompt_builder,
            qa_cache=mock_qa_cache,
            warmup_thresholds=warmup_thresholds
        )
        curriculum_service._parser = mock_parser
        
        planning_service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        critic_service = CriticService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Mock responses
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.parse_reply.return_value = Mock(
            task="Craft diamond pickaxe",
            context="You need diamonds to craft this"
        )
        mock_parser.extract_main_function.return_value = Mock(
            program_code="async function craftDiamondPickaxe() { /* code */ }",
            exec_code="await craftDiamondPickaxe();"
        )
        mock_parser.extract_critique.return_value = Mock(
            success=False,
            critique="Failed to craft diamond pickaxe - no diamonds available"
        )
        
        # Execute workflow
        task_proposal = curriculum_service.next_task(sample_event, mock_chest_repo)
        intention = planning_service.plan(sample_belief, sample_desire, sample_context)
        
        # Simulate failed execution
        failed_result = Event(
            position={"x": 0, "y": 64, "z": 0},
            inventory={"wooden_pickaxe": 1},  # No diamonds
            health=20.0,
            hunger=20.0,
            biome="plains",
            nearby_blocks=["grass", "dirt"],
            nearby_entities={}
        )
        
        critique = critic_service.evaluate(intention, failed_result, sample_context)
        assert critique.success is False
        
        # Update progress (failure)
        curriculum_service.update_progress(task_proposal, success=False)
        assert task_proposal.task in curriculum_service._failed

    def test_curriculum_progression_with_warmup(self, mock_llm, mock_qa_llm, mock_prompt_builder,
                                               mock_qa_prompt_builder, mock_parser, mock_qa_cache,
                                               mock_chest_repo, warmup_thresholds, sample_event):
        """Test curriculum progression through warmup thresholds"""
        
        curriculum_service = CurriculumService(
            llm=mock_llm,
            qa_llm=mock_qa_llm,
            proposal_prompt_builder=mock_prompt_builder,
            qa_prompt_builder=mock_qa_prompt_builder,
            qa_cache=mock_qa_cache,
            warmup_thresholds=warmup_thresholds
        )
        curriculum_service._parser = mock_parser
        
        # Mock responses for different task proposals
        mock_llm.chat.return_value = "Mock LLM response"
        
        # Test initial state (no completed tasks)
        assert len(curriculum_service._completed) == 0
        assert curriculum_service._warmup.context == 15
        
        # Complete some tasks to test warmup progression
        tasks = [
            TaskProposal(task="Mine 1 wood log", context="Basic wood gathering"),
            TaskProposal(task="Craft wooden pickaxe", context="Basic tool crafting"),
            TaskProposal(task="Mine 5 stone blocks", context="Stone gathering"),
            TaskProposal(task="Craft stone pickaxe", context="Better tool crafting"),
            TaskProposal(task="Find iron ore", context="Resource exploration")
        ]
        
        # Complete tasks one by one
        for i, task in enumerate(tasks):
            curriculum_service.update_progress(task, success=True)
            assert len(curriculum_service._completed) == i + 1
            
            # Test that failed tasks are properly managed
            if i % 2 == 0:  # Every other task fails
                failed_task = TaskProposal(task=f"Failed task {i}", context="This will fail")
                curriculum_service.update_progress(failed_task, success=False)
                assert failed_task.task in curriculum_service._failed

    def test_error_handling_in_workflow(self, mock_llm, mock_qa_llm, mock_prompt_builder,
                                       mock_qa_prompt_builder, mock_parser, mock_qa_cache,
                                       mock_chest_repo, mock_obs_builder, warmup_thresholds,
                                       sample_event, sample_belief, sample_desire, sample_context):
        """Test error handling throughout the workflow"""
        
        # Setup services
        curriculum_service = CurriculumService(
            llm=mock_llm,
            qa_llm=mock_qa_llm,
            proposal_prompt_builder=mock_prompt_builder,
            qa_prompt_builder=mock_qa_prompt_builder,
            qa_cache=mock_qa_cache,
            warmup_thresholds=warmup_thresholds
        )
        curriculum_service._parser = mock_parser
        
        planning_service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        critic_service = CriticService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser
        )
        
        # Test LLM error in curriculum
        mock_llm.chat.side_effect = Exception("LLM service down")
        with pytest.raises(ProposalError):
            curriculum_service.next_task(sample_event, mock_chest_repo)
        
        # Reset mock and test parser error in planning
        mock_llm.chat.side_effect = None
        mock_llm.chat.return_value = "Mock response"
        mock_parser.extract_main_function.side_effect = Exception("Parse error")
        
        with pytest.raises(PlanningError):
            planning_service.plan(sample_belief, sample_desire, sample_context)
        
        # Reset mock and test critic error
        mock_parser.extract_main_function.side_effect = None
        mock_parser.extract_critique.side_effect = Exception("Critic parse error")
        
        intention = Intention(code="test()", exec_snippet="await test();")
        result_event = Event(
            position={"x": 0, "y": 64, "z": 0},
            inventory={"stone": 1},
            health=20.0,
            hunger=20.0,
            biome="plains",
            nearby_blocks=[],
            nearby_entities={}
        )
        
        with pytest.raises(CriticError):
            critic_service.evaluate(intention, result_event, sample_context)

    def test_chest_integration_in_workflow(self, mock_llm, mock_qa_llm, mock_prompt_builder,
                                          mock_qa_prompt_builder, mock_parser, mock_qa_cache,
                                          mock_chest_repo, mock_obs_builder, warmup_thresholds,
                                          sample_event, sample_belief, sample_desire, sample_context):
        """Test chest repository integration in the workflow"""
        
        # Setup services
        curriculum_service = CurriculumService(
            llm=mock_llm,
            qa_llm=mock_qa_llm,
            proposal_prompt_builder=mock_prompt_builder,
            qa_prompt_builder=mock_qa_prompt_builder,
            qa_cache=mock_qa_cache,
            warmup_thresholds=warmup_thresholds
        )
        curriculum_service._parser = mock_parser
        
        planning_service = PlanningService(
            llm=mock_llm,
            prompt_builder=mock_prompt_builder,
            parser=mock_parser,
            chest_repo=mock_chest_repo,
            obs_builder=mock_obs_builder
        )
        
        # Mock chest data
        mock_chest_repo.get_chests.return_value = [
            Mock(position={"x": 10, "y": 64, "z": 10}, items={"stone": 20, "wood": 15}),
            Mock(position={"x": 20, "y": 64, "z": 20}, items={})
        ]
        
        # Mock responses
        mock_llm.chat.return_value = "Mock LLM response"
        mock_parser.parse_reply.return_value = Mock(
            task="Store items in chest",
            context="Organize inventory"
        )
        mock_parser.extract_main_function.return_value = Mock(
            program_code="async function storeItems() { /* code */ }",
            exec_code="await storeItems();"
        )
        
        # Execute workflow with chest integration
        task_proposal = curriculum_service.next_task(sample_event, mock_chest_repo)
        intention = planning_service.plan(sample_belief, sample_desire, sample_context)
        
        # Verify chest repository was used
        mock_chest_repo.get_chests.assert_called()
        mock_obs_builder.build_observation.assert_called()
        
        assert isinstance(task_proposal, TaskProposal)
        assert isinstance(intention, Intention) 