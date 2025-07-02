class PlanningError(Exception):
    pass

class LLMError(Exception):
    pass

class ParserError(Exception):
    pass

class ChestRepositoryError(Exception):
    pass

class AgentError(Exception):
    """Base class for exceptions in this application."""
    pass

class CodeExecutionError(AgentError):
    """Raised when code execution fails."""
    pass