from domain.ports import GameEnvironmentPort
from infrastructure.adapters.game.minecraft.mineflayer_api_client import MineflayerAPIClient
from infrastructure.adapters.game.minecraft.mineflayer_process import MineflayerProcessManager
from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder
from domain.models import CodeSnippet, Skill
import logging

class MineflayerEnvironment(GameEnvironmentPort):
    def __init__(self, api_client: MineflayerAPIClient, 
                 process_manager: MineflayerProcessManager,
                 observation_builder: MinecraftObservationBuilder):
        self._client = api_client
        self._process = process_manager
        self._observation_builder = observation_builder
        self._logger = logging.getLogger(__name__)
        self._connected = False

    def reset(self, options=None) -> dict:
        self._process.start()
        response = self._client.start(options)
        self._logger.info(f"Reset successful. State: {response}")
        self._connected = True
        return self._observation_builder.build(events=response)


    def step(self, code_snippet: CodeSnippet, helper_functions: list[Skill]) -> dict:
        if not self._connected:
            raise RuntimeError("Not connected. Call reset() first.")
        
        # construct the code to execute this time by merge exectuion code and main function in code snippet
        code_to_execute = f"{code_snippet.main_function_code}\n{code_snippet.execution_code}"
        
        response = self._client.step({
            "code": code_to_execute, 
            "programs": "\n".join(helper_function.code for helper_function in helper_functions)
        })
        print(f"MineflayerEnvironment: response: {response}")
        return self._observation_builder.build(events=response)

    def close(self) -> None:
        if self._connected:
            self._client.stop()
        self._process.stop()
        self._connected = False

if __name__ == "__main__":

    from pathlib import Path
    from infrastructure.adapters.game.minecraft.minecraft_observation_builder import MinecraftObservationBuilder

    script_path = Path(__file__).parent / "mineflayer_server/index.js"
    api_client = MineflayerAPIClient("localhost", 3000)
    process_manager = MineflayerProcessManager(Path(script_path), logging.getLogger(__name__))
    observation_builder = MinecraftObservationBuilder()
    environment_adapter = MineflayerEnvironment(api_client, process_manager, observation_builder)
    event1 =environment_adapter.reset({
        "port": 25565,
        "waitTicks": 5,
        "reset": "hard"
    })

    code_snippet = CodeSnippet(
        function_name="chat",
        code="bot.chat('Hello, world!')"
    )
    helper_functions = [
        CodeSnippet(
            function_name="chat",
            code="bot.chat('Hello, world!')"
        )
    ]

    observation = environment_adapter.step(code_snippet, helper_functions)
    print(observation)

    environment_adapter.close()