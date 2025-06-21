from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Intention:
    """
    Represents the agent's intention or planned action.
    
    This is a value object that encapsulates what the agent
    intends to do, including the specific steps and reasoning.
    """
    action: str
    steps: List[str]
    reasoning: str
    confidence: float
    
    def __post_init__(self):
        """Validate the intention after initialization."""
        if not self.action or not self.action.strip():
            raise ValueError("Action cannot be empty")
        
        if not isinstance(self.steps, list):
            raise ValueError("Steps must be a list")
        
        if not self.steps:
            raise ValueError("Steps cannot be empty")
        
        if not self.reasoning or not self.reasoning.strip():
            raise ValueError("Reasoning cannot be empty")
        
        if not isinstance(self.confidence, (int, float)) or self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be a number between 0 and 1")
    
    @property
    def action_text(self) -> str:
        """Get the action text (cleaned)."""
        return self.action.strip()
    
    @property
    def reasoning_text(self) -> str:
        """Get the reasoning text (cleaned)."""
        return self.reasoning.strip()
    
    @property
    def step_count(self) -> int:
        """Get the number of steps in the intention."""
        return len(self.steps)
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this intention has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def is_medium_confidence(self) -> bool:
        """Check if this intention has medium confidence."""
        return 0.4 <= self.confidence < 0.8
    
    @property
    def is_low_confidence(self) -> bool:
        """Check if this intention has low confidence."""
        return self.confidence < 0.4
    
    @property
    def is_movement_action(self) -> bool:
        """Check if this is a movement action."""
        movement_keywords = ["move", "walk", "run", "jump", "climb", "swim", "fly"]
        return any(keyword in self.action.lower() for keyword in movement_keywords)
    
    @property
    def is_interaction_action(self) -> bool:
        """Check if this is an interaction action."""
        interaction_keywords = ["use", "open", "close", "activate", "deactivate", "toggle"]
        return any(keyword in self.action.lower() for keyword in interaction_keywords)
    
    @property
    def is_combat_action(self) -> bool:
        """Check if this is a combat action."""
        combat_keywords = ["attack", "defend", "dodge", "block", "strike", "hit"]
        return any(keyword in self.action.lower() for keyword in combat_keywords)
    
    @property
    def is_crafting_action(self) -> bool:
        """Check if this is a crafting action."""
        crafting_keywords = ["craft", "make", "create", "build", "assemble"]
        return any(keyword in self.action.lower() for keyword in crafting_keywords)
    
    def get_action_type(self) -> str:
        """Get the type of action."""
        if self.is_movement_action:
            return "movement"
        elif self.is_interaction_action:
            return "interaction"
        elif self.is_combat_action:
            return "combat"
        elif self.is_crafting_action:
            return "crafting"
        else:
            return "other"
    
    def get_confidence_level(self) -> str:
        """Get the confidence level as a string."""
        if self.is_high_confidence:
            return "high"
        elif self.is_medium_confidence:
            return "medium"
        else:
            return "low"
    
    def get_confidence_description(self) -> str:
        """Get a human-readable confidence description."""
        if self.is_high_confidence:
            return "Very confident in this action"
        elif self.is_medium_confidence:
            return "Somewhat confident in this action"
        else:
            return "Not very confident in this action"
    
    def get_steps_summary(self) -> str:
        """Get a summary of the steps."""
        if len(self.steps) == 1:
            return f"Step: {self.steps[0]}"
        else:
            return f"Steps ({self.step_count}): {'; '.join(self.steps)}"
    
    def is_simple_action(self) -> bool:
        """Check if this is a simple action (single step)."""
        return self.step_count == 1
    
    def is_complex_action(self) -> bool:
        """Check if this is a complex action (multiple steps)."""
        return self.step_count > 3
    
    def __str__(self) -> str:
        """String representation of the intention."""
        return (f"Intention: {self.action_text} "
                f"(Confidence: {self.get_confidence_level()})")
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Intention(action='{self.action_text}', "
                f"steps={self.steps}, reasoning='{self.reasoning_text}', "
                f"confidence={self.confidence})")
