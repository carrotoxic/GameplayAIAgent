from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Event:
    biome: str                
    time: str                 
    nearby_blocks: List[str]  
    other_blocks: List[str]
    nearby_entities: Dict[str, float]  
    health: float             
    hunger: float             
    position: Dict[str, float]         
    equipment: Dict[str, str]      
    inventory: Dict[str, int]
    chests: List[str]