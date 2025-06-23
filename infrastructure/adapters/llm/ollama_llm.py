from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama

from domain.ports.llm_port import LLMPort
from domain.models import Message
from typing import Sequence


class LangchainOllamaLLM(LLMPort):
    def __init__(self, model_name: str = "llama3"):
        self.llm = ChatOllama(model=model_name)

    def chat(self, messages: Sequence[Message]) -> Message:
        langchain_messages = [self._to_langchain(message) for message in messages]
        response = self.llm.invoke(langchain_messages)
        return Message(role="assistant", content=response.content)

    def _to_langchain(self, m: Message):
        if m.role == "system":
            return SystemMessage(content=m.content)
        elif m.role == "user":
            return HumanMessage(content=m.content)
        elif m.role == "assistant":
            return AIMessage(content=m.content)
        else:
            raise ValueError(f"Unknown role: {m.role}")
