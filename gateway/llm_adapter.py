"""LLM adapter abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseLLMAdapter(ABC):
    @abstractmethod
    def run(
        self,
        system_prompt: str,
        user_message: str,
        tools: list | None = None,
        output_type: type[BaseModel] | None = None,
        max_turns: int = 12,
    ) -> dict:
        ...

    @abstractmethod
    def chat_turn(self, messages: list[dict]) -> str:
        ...
