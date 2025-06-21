from dataclasses import dataclass

@dataclass(frozen=True)
class Observation:
    context: str
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
    completed_tasks: str
    failed_tasks: str

    def __str__(self) -> str:
        """convert to human readable text"""
        return (
            f"{self.context}"
            f"{self.biome}\n"
            f"{self.time}\n"
            f"{self.nearby_blocks}\n"
            f"{self.other_blocks}\n"
            f"{self.nearby_entities}\n"
            f"{self.health}\n"
            f"{self.hunger}\n"
            f"{self.position}\n"
            f"{self.equipment}\n"
            f"{self.inventory}\n"
            f"{self.chests}\n"
            f"Completed tasks: {self.completed_tasks or 'None'}\n"
            f"Failed tasks: {self.failed_tasks or 'None'}"
        )