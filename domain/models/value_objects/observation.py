from dataclasses import dataclass
from typing import Optional

@dataclass
class Observation:
    biome: str                
    time: str                 
    nearby_blocks: str 
    other_blocks: str
    nearby_entities: str  
    health: str             
    hunger: str             
    position: dict
    equipment: str      
    inventory: str
    chests: dict[str, object]

    error_message: str = ""
    chat_message: str = ""

    def __str__(self) -> str:
        """convert to human readable text"""
        parts = []

        if self.error_message:
            parts.append(f"Execution error: [{self.error_message}]\n")
        if self.chat_message:
            parts.append(f"Chat log: [{self.chat_message}]\n")

        parts += [
            f"Biome: {self.biome}\n",
            f"Time: {self.time}\n",
            f"Nearby blocks: {self.nearby_blocks}\n",
            f"Other blocks: {self.other_blocks}\n",
            f"Nearby entities: {self.nearby_entities}\n",
            f"Health: {self.health}\n",
            f"Hunger: {self.hunger}\n",
            f"Position: x={self.position['x']:.1f}, y={self.position['y']:.1f}, z={self.position['z']:.1f}\n" if self.position else "Position: None\n",
            f"Equipment: {self.equipment}\n",
            f"Inventory: {self.inventory}\n",
            f"Chests: {self.chests}",
        ]
        return "".join(parts)

    # you can only set the error message when the code snippet is None
    def set_error_message(self, msg: str) -> None:
        object.__setattr__(self, "error_message", msg)
    
    def set_chests(self, chests: dict[str, object]) -> None:
        object.__setattr__(self, "chests", chests)

    def copy(self) -> "Observation":
        return Observation(
            biome=self.biome,
            time=self.time,
            nearby_blocks=self.nearby_blocks,
            other_blocks=self.other_blocks,
            nearby_entities=self.nearby_entities,
            health=self.health,
            hunger=self.hunger,
            position=self.position.copy() if self.position else None,
            equipment=self.equipment,
            inventory=self.inventory,
            chests=self.chests.copy(),
            error_message=self.error_message,
            chat_message=self.chat_message,
        )