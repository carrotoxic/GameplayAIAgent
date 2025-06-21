from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from domain.models import Task


class ExecutorPort(ABC):
    """
    Hexagonal *outbound* port for executing tasks in the game environment.
    
    This port provides an interface for executing actions and
    receiving feedback from the game environment.
    """
    
    @abstractmethod
    def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task in the game environment.
        
        Args:
            task: The task to execute
            
        Returns:
            Dictionary containing execution results and feedback
        """
        ...
    
    @abstractmethod
    def execute_action(self, action: str) -> Dict[str, Any]:
        """
        Execute a single action in the game environment.
        
        Args:
            action: The action to execute (e.g., "move forward", "mine stone")
            
        Returns:
            Dictionary containing execution results
        """
        ...
    
    @abstractmethod
    def execute_script(self, script: str) -> Dict[str, Any]:
        """
        Execute a JavaScript script in the game environment.
        
        Args:
            script: The JavaScript code to execute
            
        Returns:
            Dictionary containing execution results
        """
        ...
    
    @abstractmethod
    def get_environment_state(self) -> Dict[str, Any]:
        """
        Get the current state of the game environment.
        
        Returns:
            Dictionary containing environment state information
        """
        ...
    
    @abstractmethod
    def is_action_valid(self, action: str) -> bool:
        """
        Check if an action is valid in the current environment.
        
        Args:
            action: The action to validate
            
        Returns:
            True if the action is valid, False otherwise
        """
        ...
    
    @abstractmethod
    def get_available_actions(self) -> List[str]:
        """
        Get a list of available actions in the current environment.
        
        Returns:
            List of available actions
        """
        ...
    
    @abstractmethod
    def reset_environment(self) -> None:
        """
        Reset the game environment to its initial state.
        """
        ...
    
    @abstractmethod
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of executed actions.
        
        Returns:
            List of execution history entries
        """
        ...
    
    @abstractmethod
    def clear_execution_history(self) -> None:
        """
        Clear the execution history.
        """
        ...
