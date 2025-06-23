from dataclasses import dataclass

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

    def __str__(self) -> str:
        """convert to human readable text"""
        return (
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