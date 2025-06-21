from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from domain.models import Event, Observation


class GameEnvPort(ABC):
    """
    Hexagonal *outbound* port for interacting with the game environment.
    
    This port provides an interface for observing the game state
    and receiving events from the Minecraft environment.
    """
    
    @abstractmethod
    def get_current_event(self) -> Event:
        """
        Get the current event from the game environment.
        
        Returns:
            Current game event
        """
        ...
    
    @abstractmethod
    def get_observation(self) -> Observation:
        """
        Get the current observation from the game environment.
        
        Returns:
            Current game observation
        """
        ...
    
    @abstractmethod
    def get_agent_position(self) -> Dict[str, float]:
        """
        Get the current position of the agent.
        
        Returns:
            Dictionary with x, y, z coordinates
        """
        ...
    
    @abstractmethod
    def get_agent_inventory(self) -> Dict[str, int]:
        """
        Get the current inventory of the agent.
        
        Returns:
            Dictionary mapping item names to quantities
        """
        ...
    
    @abstractmethod
    def get_agent_health(self) -> float:
        """
        Get the current health of the agent.
        
        Returns:
            Health value (0-20)
        """
        ...
    
    @abstractmethod
    def get_agent_hunger(self) -> float:
        """
        Get the current hunger level of the agent.
        
        Returns:
            Hunger value (0-20)
        """
        ...
    
    @abstractmethod
    def get_current_biome(self) -> str:
        """
        Get the current biome the agent is in.
        
        Returns:
            Biome name
        """
        ...
    
    @abstractmethod
    def get_nearby_blocks(self) -> List[str]:
        """
        Get the blocks near the agent.
        
        Returns:
            List of nearby block types
        """
        ...
    
    @abstractmethod
    def get_nearby_entities(self) -> Dict[str, float]:
        """
        Get the entities near the agent.
        
        Returns:
            Dictionary mapping entity names to distances
        """
        ...
    
    @abstractmethod
    def is_night_time(self) -> bool:
        """
        Check if it's currently night time.
        
        Returns:
            True if it's night, False otherwise
        """
        ...
    
    @abstractmethod
    def is_raining(self) -> bool:
        """
        Check if it's currently raining.
        
        Returns:
            True if it's raining, False otherwise
        """
        ...
    
    @abstractmethod
    def get_time_of_day(self) -> str:
        """
        Get the current time of day.
        
        Returns:
            Time of day description (e.g., "day", "night", "dawn", "dusk")
        """
        ...
    
    @abstractmethod
    def get_weather_conditions(self) -> Dict[str, Any]:
        """
        Get current weather conditions.
        
        Returns:
            Dictionary containing weather information
        """
        ...
    
    @abstractmethod
    def is_agent_in_danger(self) -> bool:
        """
        Check if the agent is in immediate danger.
        
        Returns:
            True if the agent is in danger, False otherwise
        """
        ...
    
    @abstractmethod
    def get_dangerous_entities_nearby(self) -> List[str]:
        """
        Get list of dangerous entities near the agent.
        
        Returns:
            List of dangerous entity names
        """
        ...
    
    @abstractmethod
    def wait_for_event(self, timeout: float = 1.0) -> Optional[Event]:
        """
        Wait for the next event from the game environment.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Next event if received within timeout, None otherwise
        """
        ...
    
    @abstractmethod
    def get_environment_summary(self) -> str:
        """
        Get a human-readable summary of the current environment.
        
        Returns:
            Environment summary string
        """
        ...
