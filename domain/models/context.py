from dataclasses import dataclass, field
from typing import List


@dataclass
class Context:
    """
    Represents the context in which the agent operates.
    
    This is a value object that contains information about
    the agent's history, current situation, and environment
    that provides context for decision making.
    """
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    current_time: str = "day"
    
    def __post_init__(self):
        """Validate the context after initialization."""
        if not isinstance(self.completed_tasks, list):
            raise ValueError("completed_tasks must be a list")
        if not isinstance(self.failed_tasks, list):
            raise ValueError("failed_tasks must be a list")
        if not isinstance(self.current_time, str):
            raise ValueError("current_time must be a string")
        
        # Ensure no duplicates
        self.completed_tasks = list(dict.fromkeys(self.completed_tasks))
        self.failed_tasks = list(dict.fromkeys(self.failed_tasks))
    
    @property
    def total_completed_tasks(self) -> int:
        """Get the total number of completed tasks."""
        return len(self.completed_tasks)
    
    @property
    def total_failed_tasks(self) -> int:
        """Get the total number of failed tasks."""
        return len(self.failed_tasks)
    
    @property
    def total_tasks(self) -> int:
        """Get the total number of tasks attempted."""
        return self.total_completed_tasks + self.total_failed_tasks
    
    @property
    def success_rate(self) -> float:
        """Get the success rate of tasks."""
        if self.total_tasks == 0:
            return 0.0
        return self.total_completed_tasks / self.total_tasks
    
    @property
    def is_night(self) -> bool:
        """Check if it's currently night time."""
        return self.current_time.lower() in ["night", "evening", "midnight"]
    
    @property
    def is_day(self) -> bool:
        """Check if it's currently day time."""
        return self.current_time.lower() in ["day", "morning", "noon", "afternoon"]
    
    def add_completed_task(self, task_name: str) -> None:
        """Add a completed task to the context."""
        if task_name not in self.completed_tasks:
            self.completed_tasks.append(task_name)
        # Remove from failed tasks if it was there
        if task_name in self.failed_tasks:
            self.failed_tasks.remove(task_name)
    
    def add_failed_task(self, task_name: str) -> None:
        """Add a failed task to the context."""
        if task_name not in self.failed_tasks:
            self.failed_tasks.append(task_name)
        # Remove from completed tasks if it was there
        if task_name in self.completed_tasks:
            self.completed_tasks.remove(task_name)
    
    def has_completed_task(self, task_name: str) -> bool:
        """Check if a specific task has been completed."""
        return task_name in self.completed_tasks
    
    def has_failed_task(self, task_name: str) -> bool:
        """Check if a specific task has failed."""
        return task_name in self.failed_tasks
    
    def has_attempted_task(self, task_name: str) -> bool:
        """Check if a specific task has been attempted."""
        return (task_name in self.completed_tasks or 
                task_name in self.failed_tasks)
    
    def get_task_status(self, task_name: str) -> str:
        """Get the status of a specific task."""
        if self.has_completed_task(task_name):
            return "completed"
        elif self.has_failed_task(task_name):
            return "failed"
        else:
            return "not_attempted"
    
    def get_recent_tasks(self, count: int = 5) -> List[str]:
        """Get the most recent completed tasks."""
        return self.completed_tasks[-count:] if self.completed_tasks else []
    
    def get_failed_tasks_summary(self) -> str:
        """Get a summary of failed tasks."""
        if not self.failed_tasks:
            return "No failed tasks"
        return f"Failed tasks: {', '.join(self.failed_tasks)}"
    
    def get_completed_tasks_summary(self) -> str:
        """Get a summary of completed tasks."""
        if not self.completed_tasks:
            return "No completed tasks"
        return f"Completed tasks: {', '.join(self.completed_tasks)}"
    
    def get_progress_summary(self) -> str:
        """Get a summary of overall progress."""
        return (f"Progress: {self.total_completed_tasks} completed, "
                f"{self.total_failed_tasks} failed "
                f"({self.success_rate:.1%} success rate)")
    
    def is_experienced(self) -> bool:
        """Check if the agent is experienced (completed many tasks)."""
        return self.total_completed_tasks >= 10
    
    def is_beginner(self) -> bool:
        """Check if the agent is a beginner (few completed tasks)."""
        return self.total_completed_tasks < 5
    
    def has_recent_failures(self) -> bool:
        """Check if the agent has recent failures."""
        return len(self.failed_tasks) > 0
    
    def get_context_summary(self) -> str:
        """Get a comprehensive context summary."""
        summary_parts = [
            f"Time: {self.current_time}",
            self.get_progress_summary(),
            self.get_completed_tasks_summary(),
            self.get_failed_tasks_summary()
        ]
        return "\n".join(summary_parts)
    
    def __str__(self) -> str:
        """String representation of the context."""
        return self.get_context_summary()
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Context(completed_tasks={self.completed_tasks}, "
                f"failed_tasks={self.failed_tasks}, "
                f"current_time='{self.current_time}')") 