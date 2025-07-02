import asyncio
import logging
from dataclasses import asdict
from typing import Optional

from domain.ports import GameEnvironmentPort
from domain.services import CriticService, CurriculumService, PlannerService, SkillService
from infrastructure.utils import load_skills
from infrastructure.websocket.agent_ws_server import manager as websocket_manager

class AgentController:
    def __init__(self, 
        curriculum_service: CurriculumService, 
        skill_service: SkillService,
        planner_service: PlannerService,
        critic_service: CriticService, 
        env: GameEnvironmentPort,
        primitive_skill_dir: str = "infrastructure/primitive_skill"
        ):
        self._curriculum_service = curriculum_service
        self._skill_service = skill_service
        self._planner_service = planner_service
        self._critic_service = critic_service
        self._env = env
        self._primitive_skill_dir = primitive_skill_dir
        self._running_task = None
        self._is_running = False

    def start(self):
        logging.info("--- AGENT START CALLED ---")
        if self._is_running:
            logging.warning("Agent is already running. Ignoring start command.")
            return

        self._is_running = True
        self._running_task = asyncio.create_task(self._run_loop())
        logging.info("Agent run loop started in background.")

    async def stop(self):
        if not self._running_task or self._running_task.done():
            print("Agent is not running.")
            return

        self._running_task.cancel()
        try:
            await self._running_task
        except asyncio.CancelledError:
            print("Agent task was successfully cancelled.")

        await self._env.close()
        self._running_task = None
        self._is_running = False
        print("Agent stopped and environment closed.")

    async def restart(self):
        await self.stop()
        self.start()

    async def _run_loop(self, max_tries_per_task: int = 5):
        try:
            logging.info(f"--- Starting agent run loop ---")
            await self._skill_service.clear()
            primitive_skillset_definitions = load_skills(self._primitive_skill_dir + "/definitions")
            primitive_skillset_usage = load_skills(self._primitive_skill_dir + "/usage")

            logging.info("Resetting environment...")
            observation = await self._env.reset({
                "port": 25565,
                "waitTicks": 5,
                "reset": "hard"
            })
            logging.info("Environment reset complete. Observation received.")
            
            # Get the first task from the curriculum service
            task = await self._curriculum_service.get_next_task(observation)
            logging.info(f"First task from curriculum: '{task.command}'")

            while task:
                logging.info(f"--- Starting task: {task.command} ---")
                try_count = 0
                success = False
                code_snippet = None
                critique: Optional[str] = None
                chest_memory = {}

                while try_count < max_tries_per_task and not success:
                    logging.info(f"--- Task attempt {try_count + 1} ---")
                    await websocket_manager.broadcast({
                        "task": task.command,
                        "code": code_snippet.function_name if code_snippet else "",
                        "observation": asdict(observation),
                        "success": success,
                        "critique": critique if critique else "",
                    })
                    logging.info("Broadcasted state to websocket.")
                    
                    retrieved_skillset = await self._skill_service.retrieve_skillset(task)
                    logging.info(f"Retrieved {len(retrieved_skillset)} skills for the task.")
                    skillset_context = primitive_skillset_usage + retrieved_skillset
                    
                    logging.info("Generating code with planner...")
                    code_snippet, llm_response = await self._planner_service.generate_code(
                        skillset_context,
                        code_snippet,
                        observation,
                        task,
                        critique
                    )

                    plan = self._planner_service._parser.extract_plan(llm_response)
                    thought = self._planner_service._parser.extract_thought(llm_response)

                    logging.info(f"code_snippet: {code_snippet}")

                    await websocket_manager.broadcast({
                        "task": asdict(task),
                        "plan": {
                            "plan": plan,
                            "thought": thought,
                            "code": code_snippet.execution_code if code_snippet else "",
                        },
                        "skills": [asdict(skill) for skill in retrieved_skillset],
                        "observation": asdict(observation),
                        "success": success,
                        "critique": critique if critique else "",
                    })

                    helper_functions = primitive_skillset_definitions + retrieved_skillset
                    if code_snippet is not None:
                        logging.info("Executing code in environment...")
                        observation = await self._env.step(code_snippet, helper_functions)
                        logging.info("Code execution finished.")
                    else:
                        logging.error("Planner failed to generate code.")
                        observation.set_error_message("Code snippet is None")
                        try_count += 1
                        continue

                    for position, chest in observation.chests.items():
                        if chest == "Invalid":
                            chest_memory.pop(position, None)
                        elif isinstance(chest, dict):
                            chest_memory[position] = chest
                    observation.set_chests(chest_memory)

                    logging.info("Evaluating with critic...")
                    success, critique = await self._critic_service.evaluate(observation, task)
                    logging.info(f"Critic evaluation: success={success}, critique='{critique}'")

                    await websocket_manager.broadcast({
                        "task": asdict(task),
                        "plan": {
                            "plan": plan,
                            "thought": thought,
                            "code": code_snippet.execution_code if code_snippet else "",
                        },
                        "skills": [asdict(skill) for skill in retrieved_skillset],
                        "observation": asdict(observation),
                        "success": success,
                        "critique": critique if critique else "",
                    })
                    logging.info("Broadcasted final state to websocket.")

                    logging.info(f"--- End of Try {try_count + 1} ---")
                    try_count += 1

                if success:
                    logging.info(f"Task '{task.command}' completed successfully.")
                    logging.info(f"Adding successful code to skill library: {code_snippet.function_name}")
                    skill = await self._skill_service.describe_skill(code=code_snippet)
                    await self._skill_service.add_skill(skill)
                    self._curriculum_service.add_completed_task(task)
                else:
                    logging.warning(f"Task '{task.command}' failed after {max_tries_per_task} attempts.")
                    self._curriculum_service.add_failed_task(task)

                # Get the next task
                task = await self._curriculum_service.get_next_task(observation)
                if task:
                    logging.info(f"New task from curriculum: '{task.command}'")
                else:
                    logging.info("Curriculum complete. No more tasks.")

        except asyncio.CancelledError:
            logging.info("Agent run loop cancelled.")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred in the run loop: {e}", exc_info=True)
            raise
        finally:
            self._is_running = False
            logging.info("--- Run loop finished. ---")


async def main():
    """A main function to run the agent controller for testing."""
    from application.composition import build_agent
    from dotenv import load_dotenv

    load_dotenv()
    
    agent_controller = None
    try:
        agent_controller = build_agent(game="minecraft")
        agent_controller.start()
        if agent_controller._running_task:
            await agent_controller._running_task
            
    except asyncio.CancelledError:
        logging.info("Main task cancelled, which is expected on shutdown.")
    except Exception as e:
        logging.error(f"An error occurred during agent execution: {e}", exc_info=True)
    finally:
        if agent_controller and agent_controller._is_running:
            logging.info("Stopping agent controller.")
            await agent_controller.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user. Shutting down.")