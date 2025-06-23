from typing import Dict, Union


#This is a service that maintains persistent environment memory across steps,
#right now it only maintains chest memory

class EnvironmentMemoryService:
    """
    Service for maintaining persistent environment memory across steps,
    such as chest contents observed in the world.
    """

    def __init__(self):
        # position (str) -> contents (dict or str)
        self._chest_memory: Dict[str, Union[dict, str]] = {}

    def update_chest_memory(self, chests: Dict[str, Union[dict, str]]) -> None:
        """
        Update internal chest memory with the latest observations.

        If a chest is marked as "Invalid", remove it.
        """
        for position, chest in chests.items():
            if chest == "Invalid":
                self._chest_memory.pop(position, None)
            else:
                self._chest_memory[position] = chest

    def get_chest_memory(self) -> Dict[str, Union[dict, str]]:
        """
        Get the full current memory of chests.
        """
        return dict(self._chest_memory)
