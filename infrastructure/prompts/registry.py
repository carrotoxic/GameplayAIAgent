from typing import Type, Dict
from domain.ports.prompt_builder_port import PromptBuilderPort

_REGISTRY: Dict[str, Type[PromptBuilderPort]] = {}

def register(name: str):
    def _decorator(cls: Type[PromptBuilderPort]):
        _REGISTRY[name] = cls
        return cls
    return _decorator

def get(name: str, **kwargs) -> PromptBuilderPort:
    if name not in _REGISTRY:
        raise KeyError(f"No PromptBuilder called '{name}'")
    return _REGISTRY[name](**kwargs)
