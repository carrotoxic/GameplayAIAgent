from domain.services import CurriculumService, CriticService, PlannerService, SkillService
# from domain.ports import GameEnvironmentPort

class AgentController:
    def __init__(self, 
        curriculum_service: CurriculumService, 
        critic_service: CriticService, 
        planner_service: PlannerService,
        skill_service: SkillService,
        # env: GameEnvironmentPort,
        ):
        self._curriculum_service = curriculum_service
        self._critic_service = critic_service
        self._planner_service = planner_service
        self._skill_service = skill_service
        # self._env = env
        self._primitive_skill_dir = "infrastructure/primitive_skill"

    def run(self, max_tries_per_task: int = 5):
        # TODO: implement environment
        # event = self._env.reset()

        '''Primitive skills refer to the core skill functions provided to the agent from the start.
            `definitions`: full function implementations, including any necessary helper logic.
            `usage`: example usage snippets of these skills, used as context for the planner/LLM.
        '''
        primitive_skillset_definitions = load_primitive_skills(self._primitive_skill_dir)
        primitive_skillset_usage = load_primitive_skills_usage(self._primitive_skill_dir)
        
        # continue to generate task until manually stopped
        while True:
            task = self._curriculum_service.next_task(event)
            print(task)

            # initialize the local variables
            try_count = 0
            success = False
            code_snippet = None
            observation = None
            critique = None
            
            # continue to generate code snippet until the task is completed or failed for max tries
            while try_count < max_tries_per_task and not success:
                # retrieve the skillset relevant to the current task
                retrieved_skillset = self._skill_service.retrieve_skillset(task)
                skillset_context = primitive_skillset_usage + retrieved_skillset
                
                # llm generate execution code based on the current situation
                code_snippet = self._planner_service.generate_code(
                    skillset_context,
                    code_snippet,
                    observation,
                    task,
                    critique
                )
    
                # execute the code snippet using both primitive skills and retrieved skills
                helper_functions = primitive_skillset_definitions + retrieved_skillset
                observation = self._env.step(code_snippet, helper_functions)

                # llm decide if the task is successful or not, and provide a critique
                critique_result = self._critic_service.evaluate(observation, task)
                success = critique_result.success
                critique = critique_result.description

                try_count += 1

            if success:
                self._skill_service.add_skill(code_snippet)
                self._curriculum_service.add_completed_task(task)
            else:
                self._curriculum_service.add_failed_task(task)



if __name__ == "__main__":

    from domain.models import Event
    from domain.services import CurriculumService, CriticService, PlannerService, SkillService
    from application.agent_controller import AgentController

    event = Event(
        position={"x": 10.5, "y": 64.0, "z": -5.2},
        inventory={"oak_log": 3, "wooden_pickaxe": 1},
        health=18.5,
        hunger=15.0,
        biome="forest",
        nearby_blocks=["grass", "dirt", "stone", "oak_log"],
        nearby_entities={"cow": 5.0},
        time="day",
        other_blocks="iron_ore",
        equipment={"helmet": "leather_helmet"},
        chests="Chest 1: iron_ingot: 8",
    )

    agent_controller = AgentController(
        curriculum_service=CurriculumService(),
        critic_service=CriticService(),
        planner_service=PlannerService(),
        skill_service=SkillService(),
    )

    agent_controller.run()