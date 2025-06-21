from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from domain.models import Skill, Task


class MemoryPort(ABC):
    """
    Hexagonal *outbound* port for persistent memory storage.
    
    This port provides an interface for storing and retrieving
    various types of data that need to persist across sessions.
    """
    
    @abstractmethod
    def save_skills(self, skills: List[Skill]) -> None:
        """
        Save skills to persistent storage.
        
        Args:
            skills: List of skills to save
        """
        ...
    
    @abstractmethod
    def load_skills(self) -> List[Skill]:
        """
        Load skills from persistent storage.
        
        Returns:
            List of loaded skills
        """
        ...
    
    @abstractmethod
    def save_task_history(self, tasks: List[Task]) -> None:
        """
        Save task history to persistent storage.
        
        Args:
            tasks: List of tasks to save
        """
        ...
    
    @abstractmethod
    def load_task_history(self) -> List[Task]:
        """
        Load task history from persistent storage.
        
        Returns:
            List of loaded tasks
        """
        ...
    
    @abstractmethod
    def save_agent_state(self, state_data: Dict[str, Any]) -> None:
        """
        Save agent state to persistent storage.
        
        Args:
            state_data: Agent state data to save
        """
        ...
    
    @abstractmethod
    def load_agent_state(self) -> Optional[Dict[str, Any]]:
        """
        Load agent state from persistent storage.
        
        Returns:
            Agent state data if found, None otherwise
        """
        ...
    
    @abstractmethod
    def save_observation(self, observation_data: Dict[str, Any]) -> None:
        """
        Save an observation to persistent storage.
        
        Args:
            observation_data: Observation data to save
        """
        ...
    
    @abstractmethod
    def load_recent_observations(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Load recent observations from persistent storage.
        
        Args:
            count: Number of observations to load
            
        Returns:
            List of recent observations
        """
        ...
    
    @abstractmethod
    def clear_all_data(self) -> None:
        """
        Clear all stored data.
        """
        ...
    
    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the storage.
        
        Returns:
            Dictionary containing storage information
        """
        ...
