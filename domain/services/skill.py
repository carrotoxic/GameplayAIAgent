from typing import List, Optional
from domain.models import Skill, TaskProposal
from domain.ports import MemoryPort


class SkillService:
    """
    Domain service for managing agent skills.
    
    Responsibilities:
    ---------------
    • Track and update skill proficiency based on task outcomes
    • Provide skill recommendations for tasks
    • Manage skill learning and decay
    ---------------
    """
    
    def __init__(self, memory: MemoryPort):
        self._memory = memory
        self._skills: List[Skill] = []
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a specific skill by name."""
        for skill in self._skills:
            if skill.skill_name.lower() == skill_name.lower():
                return skill
        return None
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills."""
        return self._skills.copy()
    
    def get_skills_by_type(self, skill_type: str) -> List[Skill]:
        """Get skills of a specific type."""
        return [skill for skill in self._skills if skill.get_skill_type() == skill_type]
    
    def get_proficient_skills(self) -> List[Skill]:
        """Get skills where the agent is proficient or better."""
        return [skill for skill in self._skills if skill.is_proficient]
    
    def get_skills_needing_practice(self) -> List[Skill]:
        """Get skills that need more practice."""
        return [skill for skill in self._skills if skill.needs_practice()]
    
    def add_skill(self, skill: Skill) -> None:
        """Add a new skill."""
        if not self.get_skill(skill.skill_name):
            self._skills.append(skill)
    
    def update_skill_proficiency(self, skill_name: str, new_proficiency: float) -> None:
        """Update the proficiency of a skill."""
        skill = se
        if skill:
            updated_skill = Skill(
                name=skill.skill_name,
                proficiency=skill.proficiency,
                usage_count=skill.usage_count + 1,
                last_used=skill.last_used
            )
            self._skills.remove(skill)
            self._skills.append(updated_skill)
    
    def learn_from_task(self, task: TaskProposal, success: bool) -> None:
        """Learn from a completed task to update relevant skills."""
        task_type = task.get_task_type()
        
        # Map task types to skill names
        skill_mapping = {
            "mining": "mining",
            "crafting": "crafting", 
            "building": "crafting",
            "combat": "combat",
            "exploration": "movement",
            "survival": "survival"
        }
        
        skill_name = skill_mapping.get(task_type, "general")
        
        # Get or create the skill
        skill = self.get_skill(skill_name)
        if not skill:
            skill = Skill(
                name=skill_name,
                proficiency=0.1,  # Start with low proficiency
                usage_count=0
            )
            self.add_skill(skill)
        
        # Update proficiency based on success
        if success:
            # Increase proficiency on success
            new_proficiency = min(1.0, skill.proficiency + 0.1)
        else:
            # Slight decrease on failure, but not below 0.1
            new_proficiency = max(0.1, skill.proficiency - 0.05)
        
        self.update_skill_proficiency(skill_name, new_proficiency)
        self.increment_skill_usage(skill_name)
    
    def get_recommended_skills_for_task(self, task: TaskProposal) -> List[Skill]:
        """Get skills that would be useful for a given task."""
        task_type = task.get_task_type()
        relevant_skills = self.get_skills_by_type(task_type)
        
        # Sort by proficiency (highest first)
        return sorted(relevant_skills, key=lambda s: s.proficiency, reverse=True)
    
    def has_required_skill(self, task: TaskProposal, min_proficiency: float = 0.3) -> bool:
        """Check if the agent has the required skill for a task."""
        relevant_skills = self.get_recommended_skills_for_task(task)
        return any(skill.proficiency >= min_proficiency for skill in relevant_skills)
    
    def get_skill_gaps(self, task: TaskProposal) -> List[str]:
        """Get skills that are missing or insufficient for a task."""
        task_type = task.get_task_type()
        relevant_skills = self.get_skills_by_type(task_type)
        
        gaps = []
        if not relevant_skills:
            gaps.append(f"No {task_type} skills")
        else:
            low_proficiency_skills = [skill for skill in relevant_skills if skill.proficiency < 0.3]
            if low_proficiency_skills:
                gaps.extend([f"Low proficiency in {skill.skill_name}" for skill in low_proficiency_skills])
        
        return gaps
    
    def get_learning_priorities(self) -> List[Skill]:
        """Get skills that should be prioritized for learning."""
        # Skills that need practice and are frequently used
        priorities = []
        
        for skill in self._skills:
            if skill.needs_practice() and skill.usage_count > 0:
                priorities.append(skill)
        
        # Sort by usage count (most used first)
        return sorted(priorities, key=lambda s: s.usage_count, reverse=True)
    
    def get_skill_summary(self) -> str:
        """Get a summary of all skills."""
        if not self._skills:
            return "No skills learned yet"
        
        summary_parts = []
        for skill_type in ["mining", "crafting", "combat", "movement", "survival"]:
            skills = self.get_skills_by_type(skill_type)
            if skills:
                avg_proficiency = sum(s.proficiency for s in skills) / len(skills)
                summary_parts.append(f"{skill_type}: {avg_proficiency:.1%} avg proficiency")
        
        return "; ".join(summary_parts)
    
    def save_skills(self) -> None:
        """Save skills to memory."""
        self._memory.save_skills(self._skills)
    
    def load_skills(self) -> None:
        """Load skills from memory."""
        self._skills = self._memory.load_skills()
