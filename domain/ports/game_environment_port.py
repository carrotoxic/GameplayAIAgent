import abc
from domain.models import CodeSnippet, Skill

class GameEnvironmentPort(abc.ABC):
    """
    Hexagonal *inbound* port for interacting with any game environment.

    Responsibilities:
    - Reset the game environment to a start state
    - Step the environment forward by executing an action
    - Optionally close/shutdown the environment
    """

    @abc.abstractmethod
    async def reset(self, options=None) -> dict:
        """Reset the environment and return the initial Event observation."""
        raise NotImplementedError

    @abc.abstractmethod
    async def step(self, code_snippet: CodeSnippet, helper_functions: list[Skill]) -> dict:
        """Execute one step in the environment using the provided action."""
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self) -> None:
        """Shutdown the environment cleanly (if needed)."""
        raise NotImplementedError
