from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Desire:
    """
    Represents the agent's current desire or goal.
    
    This is a value object that encapsulates what the agent
    wants to achieve, along with its priority level.
    """
    goal: str
    priority: float
    
    def __post_init__(self):
        """Validate the desire after initialization."""
        if not self.goal or not self.goal.strip():
            raise ValueError("Goal cannot be empty")
        
        if not isinstance(self.priority, (int, float)) or self.priority < 0 or self.priority > 1:
            raise ValueError("Priority must be a number between 0 and 1")
    
    @property
    def goal_text(self) -> str:
        """Get the goal text (cleaned)."""
        return self.goal.strip()
    
    @property
    def is_high_priority(self) -> bool:
        """Check if this is a high priority desire."""
        return self.priority >= 0.8
    
    @property
    def is_medium_priority(self) -> bool:
        """Check if this is a medium priority desire."""
        return 0.4 <= self.priority < 0.8
    
    @property
    def is_low_priority(self) -> bool:
        """Check if this is a low priority desire."""
        return self.priority < 0.4
    
    @property
    def is_survival_goal(self) -> bool:
        """Check if this is a survival-related goal."""
        survival_keywords = ["eat", "heal", "health", "hunger", "survive", "escape", "hide"]
        return any(keyword in self.goal.lower() for keyword in survival_keywords)
    
    @property
    def is_exploration_goal(self) -> bool:
        """Check if this is an exploration-related goal."""
        exploration_keywords = ["explore", "find", "discover", "search", "look", "investigate"]
        return any(keyword in self.goal.lower() for keyword in exploration_keywords)
    
    @property
    def is_crafting_goal(self) -> bool:
        """Check if this is a crafting-related goal."""
        crafting_keywords = ["craft", "make", "create", "build", "construct"]
        return any(keyword in self.goal.lower() for keyword in crafting_keywords)
    
    @property
    def is_mining_goal(self) -> bool:
        """Check if this is a mining-related goal."""
        mining_keywords = ["mine", "dig", "extract", "gather", "collect"]
        return any(keyword in self.goal.lower() for keyword in mining_keywords)
    
    @property
    def is_combat_goal(self) -> bool:
        """Check if this is a combat-related goal."""
        combat_keywords = ["kill", "attack", "fight", "defeat", "eliminate"]
        return any(keyword in self.goal.lower() for keyword in combat_keywords)
    
    def get_goal_type(self) -> str:
        """Get the type of goal."""
        if self.is_survival_goal:
            return "survival"
        elif self.is_exploration_goal:
            return "exploration"
        elif self.is_crafting_goal:
            return "crafting"
        elif self.is_mining_goal:
            return "mining"
        elif self.is_combat_goal:
            return "combat"
        else:
            return "other"
    
    def get_priority_level(self) -> str:
        """Get the priority level as a string."""
        if self.is_high_priority:
            return "high"
        elif self.is_medium_priority:
            return "medium"
        else:
            return "low"
    
    def get_priority_description(self) -> str:
        """Get a human-readable priority description."""
        if self.is_high_priority:
            return "Urgent - must be done immediately"
        elif self.is_medium_priority:
            return "Important - should be done soon"
        else:
            return "Optional - can be done later"
    
    def is_urgent(self) -> bool:
        """Check if this desire is urgent (very high priority)."""
        return self.priority >= 0.9
    
    def is_optional(self) -> bool:
        """Check if this desire is optional (low priority)."""
        return self.priority <= 0.3
    
    def __str__(self) -> str:
        """String representation of the desire."""
        return f"Desire: {self.goal_text} (Priority: {self.get_priority_level()})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Desire(goal='{self.goal_text}', priority={self.priority})"
