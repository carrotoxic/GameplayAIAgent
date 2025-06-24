from domain.services import CurriculumService, CriticService, PlannerService, SkillService
from domain.models import Event   # TODO: change to Observation
from infrastructure.utils import load_skills
# from domain.ports import GameEnvironmentPort

class AgentController:
    def __init__(self, 
        curriculum_service: CurriculumService, 
        skill_service: SkillService,
        planner_service: PlannerService,
        critic_service: CriticService, 
        # env: GameEnvironmentPort,
        primitive_skill_dir: str = "infrastructure/primitive_skill"
        ):
        self._curriculum_service = curriculum_service
        self._skill_service = skill_service
        self._planner_service = planner_service
        self._critic_service = critic_service
        # self._env = env
        self._primitive_skill_dir = primitive_skill_dir

    def run(self, max_tries_per_task: int = 5):
        # TODO: implement environment
        # event = self._env.reset()
        '''dummy event'''
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

        '''
        Primitive skills refer to the core skill functions provided to the agent from the start.
            `definitions`: full function implementations, including any necessary helper logic.
            `usage`: example usage snippets of these skills, used as context for the planner/LLM.
          Return a list of Skill Value Objects
        '''

        print("AgentController: loading primitive skills")
        primitive_skillset_definitions = load_skills(self._primitive_skill_dir + "/definitions")
        primitive_skillset_usage = load_skills(self._primitive_skill_dir + "/usage")
        print("AgentController: primitive skills loaded")
        # continue to generate task until manually stopped
        while True:
            print("AgentController: generating task")
            task = self._curriculum_service.next_task(event)
            print(f"AgentController: task: {task.command}")

            # initialize the local variables
            try_count = 0
            success = False
            code_snippet = None
            observation = None
            critique = None
            
            # continue to generate code snippet until the task is completed or failed for max tries
            while try_count < max_tries_per_task and not success:
                print("AgentController: retrieving skillset")
                # retrieve the skillset relevant to the current task
                retrieved_skillset = self._skill_service.retrieve_skillset(task)
                print(f"AgentController: skillset retrieved: {retrieved_skillset}")
                skillset_context = primitive_skillset_usage + retrieved_skillset
                
                # llm generate execution code based on the current situation
                print("AgentController: generating code snippet")
                code_snippet = self._planner_service.generate_code(
                    skillset_context,
                    code_snippet,
                    observation,
                    task,
                    critique
                )
                print(f"AgentController: code snippet generated: {code_snippet}")
                # execute the code snippet using both primitive skills and retrieved skills
                helper_functions = primitive_skillset_definitions + retrieved_skillset
                print("AgentController: helper functions generated")
                # TODO: implement environment
                print("AgentController: executing code snippet")
                # observation = self._env.step(code_snippet, helper_functions)
                print("AgentController: observation generated")

                # llm decide if the task is successful or not, and provide a critique
                print("AgentController: evaluating task")
                success, critique = self._critic_service.evaluate(observation, task)
                print("AgentController: task evaluated")

                print(f"================================================")
                print(f"AgentController: success: {success}")
                print(f"AgentController: critique: {critique}")
                print(f"================================================")
                try_count += 1
                print(f"AgentController: try count: {try_count}")

            if success:
                print("AgentController: task completed")
                self._skill_service.add_skill(code_snippet)
                self._curriculum_service.add_completed_task(task)
            else:
                print("AgentController: task failed")
                self._curriculum_service.add_failed_task(task)



if __name__ == "__main__":

    # from domain.models import Event
    from application.composition import build_agent

    agent_controller = build_agent(game="minecraft")

    agent_controller.run(max_tries_per_task=3)