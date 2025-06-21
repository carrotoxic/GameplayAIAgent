from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Skill:
    """
    Represents a skill that the agent has learned or can perform.
    
    This is a value object that encapsulates the agent's
    capabilities, including proficiency level and usage history.
    """
    name: str
    proficiency: float
    usage_count: int
    last_used: Optional[str] = None
    
    def __post_init__(self):
        """Validate the skill after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Skill name cannot be empty")
        
        if not isinstance(self.proficiency, (int, float)) or self.proficiency < 0 or self.proficiency > 1:
            raise ValueError("Proficiency must be a number between 0 and 1")
        
        if not isinstance(self.usage_count, int) or self.usage_count < 0:
            raise ValueError("Usage count must be a non-negative integer")
    
    @property
    def skill_name(self) -> str:
        """Get the skill name (cleaned)."""
        return self.name.strip()
    
    @property
    def is_expert(self) -> bool:
        """Check if the agent is an expert in this skill."""
        return self.proficiency >= 0.9
    
    @property
    def is_proficient(self) -> bool:
        """Check if the agent is proficient in this skill."""
        return self.proficiency >= 0.7
    
    @property
    def is_competent(self) -> bool:
        """Check if the agent is competent in this skill."""
        return self.proficiency >= 0.5
    
    @property
    def is_beginner(self) -> bool:
        """Check if the agent is a beginner in this skill."""
        return self.proficiency < 0.3
    
    @property
    def is_unused(self) -> bool:
        """Check if the skill has never been used."""
        return self.usage_count == 0
    
    @property
    def is_frequently_used(self) -> bool:
        """Check if the skill is frequently used."""
        return self.usage_count >= 10
    
    @property
    def is_mining_skill(self) -> bool:
        """Check if this is a mining-related skill."""
        mining_skills = ["mining", "digging", "extraction", "ore_finding"]
        return any(skill in self.skill_name.lower() for skill in mining_skills)
    
    @property
    def is_crafting_skill(self) -> bool:
        """Check if this is a crafting-related skill."""
        crafting_skills = ["crafting", "building", "construction", "assembly"]
        return any(skill in self.skill_name.lower() for skill in crafting_skills)
    
    @property
    def is_combat_skill(self) -> bool:
        """Check if this is a combat-related skill."""
        combat_skills = ["combat", "fighting", "weapon_use", "defense"]
        return any(skill in self.skill_name.lower() for skill in combat_skills)
    
    @property
    def is_movement_skill(self) -> bool:
        """Check if this is a movement-related skill."""
        movement_skills = ["movement", "navigation", "climbing", "swimming"]
        return any(skill in self.skill_name.lower() for skill in movement_skills)
    
    @property
    def is_survival_skill(self) -> bool:
        """Check if this is a survival-related skill."""
        survival_skills = ["survival", "healing", "cooking", "farming"]
        return any(skill in self.skill_name.lower() for skill in survival_skills)
    
    def get_skill_type(self) -> str:
        """Get the type of skill."""
        if self.is_mining_skill:
            return "mining"
        elif self.is_crafting_skill:
            return "crafting"
        elif self.is_combat_skill:
            return "combat"
        elif self.is_movement_skill:
            return "movement"
        elif self.is_survival_skill:
            return "survival"
        else:
            return "other"
    
    def get_proficiency_level(self) -> str:
        """Get the proficiency level as a string."""
        if self.is_expert:
            return "expert"
        elif self.is_proficient:
            return "proficient"
        elif self.is_competent:
            return "competent"
        elif self.is_beginner:
            return "beginner"
        else:
            return "novice"
    
    def get_proficiency_description(self) -> str:
        """Get a human-readable proficiency description."""
        if self.is_expert:
            return "Mastered this skill"
        elif self.is_proficient:
            return "Very good at this skill"
        elif self.is_competent:
            return "Adequate at this skill"
        elif self.is_beginner:
            return "Learning this skill"
        else:
            return "Just starting with this skill"
    
    def get_usage_description(self) -> str:
        """Get a human-readable usage description."""
        if self.is_unused:
            return "Never used"
        elif self.usage_count == 1:
            return "Used once"
        elif self.is_frequently_used:
            return f"Used {self.usage_count} times (frequently)"
        else:
            return f"Used {self.usage_count} times"
    
    def needs_practice(self) -> bool:
        """Check if the skill needs more practice."""
        return self.proficiency < 0.5 and self.usage_count < 5
    
    def is_rusty(self) -> bool:
        """Check if the skill might be rusty (high proficiency but low recent usage)."""
        return self.proficiency >= 0.7 and self.usage_count < 3
    
    def get_skill_summary(self) -> str:
        """Get a comprehensive skill summary."""
        return (f"{self.skill_name} ({self.get_skill_type()}): "
                f"{self.get_proficiency_level()} - {self.get_usage_description()}")
    
    def __str__(self) -> str:
        """String representation of the skill."""
        return self.get_skill_summary()
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Skill(name='{self.skill_name}', proficiency={self.proficiency}, "
                f"usage_count={self.usage_count}, last_used='{self.last_used}')")
