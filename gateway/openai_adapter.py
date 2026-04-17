"""OpenAI-based LLM adapter implementation."""

from __future__ import annotations

import inspect
import json
from typing import Any, Callable

from pydantic import BaseModel

from gateway.llm_adapter import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter that delegates to the OpenAI chat-completions API."""

    def __init__(self, model: str = "gpt-4.1", client: Any | None = None):
        if client is None:
            from openai import OpenAI
            client = OpenAI()
        self.client = client
        self.model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        system_prompt: str,
        user_message: str,
        tools: list | None = None,
        output_type: type[BaseModel] | None = None,
        max_turns: int = 12,
    ) -> dict:
        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        tool_defs = self._build_tool_defs(tools) if tools else None
        tool_map = {fn.__name__: fn for fn in (tools or [])}

        for _ in range(max_turns):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
            }
            if tool_defs:
                kwargs["tools"] = tool_defs

            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" or (
                hasattr(choice.message, "tool_calls") and choice.message.tool_calls
            ):
                messages.append(choice.message)
                for tc in choice.message.tool_calls:
                    fn = tool_map.get(tc.function.name)
                    if fn is None:
                        result = json.dumps({"error": f"Unknown tool: {tc.function.name}"})
                    else:
                        args = json.loads(tc.function.arguments)
                        result = str(fn(**args))
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        }
                    )
                continue

            # Final text response
            content = choice.message.content or ""
            if output_type is not None:
                try:
                    parsed = json.loads(content)
                    return output_type(**parsed).model_dump()
                except Exception:
                    return {"raw": content}
            return {"response": content}

        return {"error": "max_turns exceeded"}

    def chat_turn(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_tool_defs(functions: list[Callable]) -> list[dict]:
        """Convert Python callables to OpenAI function-tool definitions."""
        defs: list[dict] = []
        for fn in functions:
            sig = inspect.signature(fn)
            params: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
            for name, param in sig.parameters.items():
                prop: dict[str, Any] = {"type": "string"}
                annotation = param.annotation
                if annotation is int:
                    prop["type"] = "integer"
                elif annotation is float:
                    prop["type"] = "number"
                elif annotation is bool:
                    prop["type"] = "boolean"
                params["properties"][name] = prop
                if param.default is inspect.Parameter.empty:
                    params["required"].append(name)

            defs.append(
                {
                    "type": "function",
                    "function": {
                        "name": fn.__name__,
                        "description": (fn.__doc__ or "").strip(),
                        "parameters": params,
                    },
                }
            )
        return defs
