from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Observation:
    biome: str                
    time: str                 
    nearby_blocks: str 
    other_blocks: str
    nearby_entities: str  
    health: str             
    hunger: str             
    position: str         
    equipment: str      
    inventory: str
    chests: str

    error_message: Optional[str] = ""
    chat_message: Optional[str] = ""

    def __str__(self) -> str:
        """convert to human readable text"""
        return (
            f"Execution error: [{self.error_message}]\n\n"
            f"Chat log: [{self.chat_message}]\n\n"
            f"Biome: {self.biome}\n\n"
            f"Time: {self.time}\n\n"
            f"Nearby blocks: {self.nearby_blocks}\n\n"
            f"Other blocks: {self.other_blocks}\n\n"
            f"Nearby entities: {self.nearby_entities}\n\n"
            f"Health: {self.health}\n\n"
            f"Hunger: {self.hunger}\n\n"
            f"Position: x={self.position['x']:.1f}, y={self.position['y']:.1f}, z={self.position['z']:.1f}\n\n"
            f"Equipment: {self.equipment}\n\n"
            f"Inventory: {self.inventory}\n\n"
            f"Chests: {self.chests}"
        )

    # you can only set the error message when the code snippet is None
    def set_error_message(self, msg: str) -> None:
        object.__setattr__(self, "error_message", msg)
    