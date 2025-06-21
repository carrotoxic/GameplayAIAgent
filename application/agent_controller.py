from domain.services import CurriculumService, CriticService, PlannerService, SkillService
from domain.ports import GameEnvironmentPort

class AgentController:
    def __init__(self, 
        curriculum_service: CurriculumService, 
        critic_service: CriticService, 
        planner_service: PlannerService,
        skill_service: SkillService,
        env: GameEnvironmentPort,
        ):
        self._curriculum_service = curriculum_service
        self._critic_service = critic_service
        self._planner_service = planner_service
        self._skill_service = skill_service
        self._env = env

    def run(self, max_tries: int = 5):
        agent_state = self._env.reset()
        
        # continue to generate task until manually stopped
        while True:
            task = self._curriculum_service.next_task(agent_state)

            # initialize the local variables
            try_count = 0
            success = False
            code_snippet = None
            environment_feedback = None
            execution_error = None
            critique = None
            
            while try_count < max_tries and not success:
                skillset = self._skill_service.get_skillset(
                    task, 
                    environment_feedback
                )
                
                code_snippet = self._planner_service.generate_code(
                    task,
                    code_snippet,
                    environment_feedback,
                    execution_error,
                    critique,
                    skillset
                )
    
                (agent_state,
                 environment_feedback,
                 execution_error
                ) = self._env.step(code_snippet)

                success, critique = self._critic_service.evaluate(
                    task,
                    agent_state,
                )

                try_count += 1

            if success:
                self._skill_service.add_skill(code_snippet)
                self._curriculum_service.add_completed_task(task)
            else:
                self._curriculum_service.add_failed_task(task)
