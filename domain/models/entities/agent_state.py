from dataclasses import dataclass
# from .belief import Belief
# from .desire import Desire
# from .context import Context

# TODO: Implement AgentState
# Agent State is a entity that holds the iternal state of the agent
# Belief is about the thing the agent believes about the world
# Desire is about the thing the agent wants to achieve

# @dataclass(frozen=True)
# class AgentState:
#     """
#     Represents the current state of the AI agent in the game world.
    
#     This is a value object that encapsulates all the information
#     the agent has about its current situation, including beliefs,
#     desires, and context.
#     """
#     belief: Belief
#     desire: Desire
#     context: Context
    
#     @property
#     def progress(self) -> int:
#         return len(self.context.completed_tasks)
   