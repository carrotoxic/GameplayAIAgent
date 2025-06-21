from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Belief:
    """
    Represents the agent's beliefs about the current state of the world.
    
    This is a value object that encapsulates what the agent believes
    to be true about its environment, inventory, and capabilities.
    """
    position: Dict[str, float]
    inventory: Dict[str, int]
    health: float
    biome: str
    nearby_blocks: Optional[List[str]] = None
    nearby_entities: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        """Validate the belief after initialization."""
        if not isinstance(self.position, dict) or len(self.position) != 3:
            raise ValueError("Position must be a dict with x, y, z coordinates")
        
        if not all(key in self.position for key in ['x', 'y', 'z']):
            raise ValueError("Position must contain x, y, z coordinates")
        
        if not isinstance(self.health, (int, float)) or self.health < 0 or self.health > 20:
            raise ValueError("Health must be a number between 0 and 20")
        
        if not self.biome or not isinstance(self.biome, str):
            raise ValueError("Biome must be a non-empty string")
    
    @property
    def x(self) -> float:
        """Get the X coordinate."""
        return self.position['x']
    
    @property
    def y(self) -> float:
        """Get the Y coordinate."""
        return self.position['y']
    
    @property
    def z(self) -> float:
        """Get the Z coordinate."""
        return self.position['z']
    
    @property
    def inventory_count(self) -> int:
        """Get the total number of items in inventory."""
        return sum(self.inventory.values())
    
    @property
    def inventory_slots_used(self) -> int:
        """Get the number of inventory slots used."""
        return len([count for count in self.inventory.values() if count > 0])
    
    @property
    def is_inventory_full(self) -> bool:
        """Check if inventory is full (36 slots)."""
        return self.inventory_slots_used >= 36
    
    @property
    def is_healthy(self) -> bool:
        """Check if the agent is healthy."""
        return self.health >= 15.0
    
    @property
    def is_critical_health(self) -> bool:
        """Check if the agent has critical health."""
        return self.health <= 5.0
    
    def has_item(self, item_name: str) -> bool:
        """Check if the agent has a specific item."""
        return item_name in self.inventory and self.inventory[item_name] > 0
    
    def get_item_count(self, item_name: str) -> int:
        """Get the count of a specific item."""
        return self.inventory.get(item_name, 0)
    
    def has_tool(self) -> bool:
        """Check if the agent has any tool."""
        tools = ["wooden_pickaxe", "stone_pickaxe", "iron_pickaxe", "diamond_pickaxe",
                "wooden_axe", "stone_axe", "iron_axe", "diamond_axe",
                "wooden_sword", "stone_sword", "iron_sword", "diamond_sword"]
        return any(self.has_item(tool) for tool in tools)
    
    def has_weapon(self) -> bool:
        """Check if the agent has any weapon."""
        weapons = ["wooden_sword", "stone_sword", "iron_sword", "diamond_sword",
                  "bow", "crossbow"]
        return any(self.has_item(weapon) for weapon in weapons)
    
    def has_food(self) -> bool:
        """Check if the agent has any food."""
        foods = ["bread", "apple", "cooked_beef", "cooked_chicken", "cooked_porkchop",
                "cooked_mutton", "cooked_rabbit", "baked_potato", "carrot", "beetroot"]
        return any(self.has_item(food) for food in foods)
    
    def has_nearby_entity(self, entity_name: str) -> bool:
        """Check if a specific entity is nearby."""
        if not self.nearby_entities:
            return False
        return entity_name in self.nearby_entities
    
    def has_nearby_block(self, block_name: str) -> bool:
        """Check if a specific block is nearby."""
        if not self.nearby_blocks:
            return False
        return block_name in self.nearby_blocks
    
    def is_underground(self) -> bool:
        """Check if the agent is underground based on Y coordinate and blocks."""
        underground_indicators = ["stone", "coal_ore", "iron_ore", "diamond_ore", "deepslate"]
        return (self.y < 60 or 
                any(indicator in block for block in (self.nearby_blocks or [])
                    for indicator in underground_indicators))
    
    def is_in_danger(self) -> bool:
        """Check if the agent is in immediate danger."""
        dangerous_entities = ["zombie", "skeleton", "spider", "creeper", "enderman"]
        return any(self.has_nearby_entity(entity) for entity in dangerous_entities)
    
    def get_position_summary(self) -> str:
        """Get a human-readable position summary."""
        return f"Position: ({self.x:.1f}, {self.y:.1f}, {self.z:.1f})"
    
    def get_inventory_summary(self) -> str:
        """Get a human-readable inventory summary."""
        if not self.inventory:
            return "Empty inventory"
        
        items = [f"{item}: {count}" for item, count in self.inventory.items() if count > 0]
        return f"Inventory ({self.inventory_slots_used}/36): {', '.join(items)}"
    
    def get_health_summary(self) -> str:
        """Get a human-readable health summary."""
        return f"Health: {self.health:.1f}/20"
    
    def __str__(self) -> str:
        """String representation of the belief."""
        return (f"Belief at {self.get_position_summary()} in {self.biome} - "
                f"{self.get_health_summary()}")
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Belief(position={self.position}, inventory={self.inventory}, "
                f"health={self.health}, biome='{self.biome}')")
