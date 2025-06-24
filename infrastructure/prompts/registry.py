from typing import Type, Dict, Callable
from domain.ports.prompt_builder_port import PromptBuilderPort

_REGISTRY: Dict[tuple[str, str], Type[PromptBuilderPort]] = {}

def register(game: str, name: str) -> Callable[[Type[PromptBuilderPort]], Type[PromptBuilderPort]]:
    """
    Decorator to register a PromptBuilder class under a given name.

    Example:
        @register("minecraft", "qa_question")
        class QAQuestionPromptBuilder(...):
            ...
    """
    
    def _decorator(cls: Type[PromptBuilderPort]):
        key = (game, name)
        if key in _REGISTRY:
            raise ValueError(f"PromptBuilder '{name}' for game '{game}' is already registered.")
        _REGISTRY[key] = cls
        return cls
    return _decorator

def get(game: str, name: str, **kwargs) -> PromptBuilderPort:
    from infrastructure.prompts import import_all_prompt_builders
    import_all_prompt_builders()
    
    key = (game, name)
    if key not in _REGISTRY:
        raise KeyError(f"No PromptBuilder called '{name}' for game '{game}'")
    return _REGISTRY[key](**kwargs)
