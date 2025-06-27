from abc import ABC, abstractmethod

class GameEnvironmentPort(ABC):
    """
    Hexagonal *inbound* port for interacting with any game environment.

    Responsibilities:
    - Reset the game environment to a start state
    - Step the environment forward by executing an action
    - Optionally close/shutdown the environment
    """

    @abstractmethod
    def reset(self, options: dict = None) -> dict:
        """Reset the environment and return the initial Event observation."""
        pass

    @abstractmethod
    def step(self, action: str = None) -> dict:
        """Execute one step in the environment using the provided action."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Shutdown the environment cleanly (if needed)."""
        pass
