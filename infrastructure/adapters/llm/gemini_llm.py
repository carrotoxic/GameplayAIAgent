from langchain_google_genai import ChatGoogleGenerativeAI
import os
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from domain.ports.llm_port import LLMPort
from domain.models import Message
from typing import Sequence


class GeminiLLM(LLMPort):
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        self.model_name = model_name
        # Defer client initialization
        self._llm = None

    @property
    def llm(self):
        # Initialize the client only when it's first accessed
        if self._llm is None:
            self._llm = ChatGoogleGenerativeAI(model=self.model_name, google_api_key=os.getenv("GOOGLE_API_KEY"))
        return self._llm

    async def chat(self, messages: Sequence[Message]) -> Message:
        langchain_messages = [self._to_langchain(message) for message in messages]
        
        # Run the synchronous invoke method in a separate thread
        response = await asyncio.to_thread(self.llm.invoke, langchain_messages)
        
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


if __name__ == "__main__":
    llm = GeminiLLM()
    print(llm.chat([Message(role="user", content="Write a haiku about AI and summer.")]))
