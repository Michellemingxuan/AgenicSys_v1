"""SafeChain adapter stub — for deployment environment with SafeChain LLM pipeline."""

from __future__ import annotations

import inspect
import json
import re
from typing import Any, Callable

from pydantic import BaseModel

from gateway.firewall_stack import FirewallRejection
from gateway.llm_adapter import BaseLLMAdapter


class SafeChainAdapter(BaseLLMAdapter):
    """Adapter for SafeChain-based LLM invocation.

    This is a stub — the actual SafeChain package is only available in the
    deployment environment. All methods raise NotImplementedError if
    safechain is not installed.
    """

    def __init__(
        self,
        llm: Any | None = None,
        model_name: str = "gpt-4.1",
        max_iterations: int = 12,
    ):
        self.llm = llm
        self.model_name = model_name
        self.max_iterations = max_iterations

    def run(
        self,
        system_prompt: str,
        user_message: str,
        tools: list | None = None,
        output_type: type[BaseModel] | None = None,
        max_turns: int = 12,
    ) -> dict:
        """Manual tool-calling loop with prompt-injected tool schemas."""
        effective_max = min(max_turns, self.max_iterations)

        if tools:
            tool_block = self._build_tool_schema_block(tools)
            system_prompt = f"{system_prompt}\n\n{tool_block}"

        tool_map = {fn.__name__: fn for fn in (tools or [])}

        messages = [
            {"role": "Context", "content": system_prompt},
            {"role": "Request", "content": user_message},
        ]

        for _ in range(effective_max):
            raw = self._invoke(messages)

            # Try to parse as JSON
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                if output_type is not None:
                    return {"raw": raw}
                return {"response": raw}

            # Check for tool call
            if "tool_call" in parsed:
                tc = parsed["tool_call"]
                fn_name = tc.get("name", "")
                fn_args = tc.get("arguments", {})

                fn = tool_map.get(fn_name)
                if fn is None:
                    result_str = json.dumps({"error": f"Unknown tool: {fn_name}"})
                else:
                    result = fn(**fn_args)
                    result_str = str(result)
                    # Truncate large results
                    if len(result_str) > 3000:
                        result_str = result_str[:3000] + "\n... (truncated)"

                messages.append({"role": "Response", "content": raw})
                messages.append({"role": "Context", "content": f"Tool result for {fn_name}: {result_str}"})
                continue

            # Check for final output
            if "output" in parsed:
                return parsed["output"] if isinstance(parsed["output"], dict) else {"response": parsed["output"]}

            # Regular JSON response
            return parsed

        return {"error": "max_iterations exceeded"}

    def chat_turn(self, messages: list[dict]) -> str:
        """Single invocation for chat-style turn."""
        # Remap roles to neutral labels
        remapped = []
        for m in messages:
            role = m.get("role", "")
            if role == "system":
                remapped.append({"role": "Context", "content": m["content"]})
            elif role == "user":
                remapped.append({"role": "Request", "content": m["content"]})
            elif role == "assistant":
                remapped.append({"role": "Response", "content": m["content"]})
            else:
                remapped.append({"role": "Context", "content": m["content"]})

        return self._invoke(remapped)

    def _invoke(self, messages: list[dict]) -> str:
        """Invoke the SafeChain LLM. Raises NotImplementedError if not available."""
        try:
            import safechain  # noqa: F401
        except ImportError:
            raise NotImplementedError(
                "SafeChain is not available in this environment. "
                "Install safechain or use OpenAIAdapter instead."
            )

        # Mask long digit sequences in messages
        masked_messages = []
        for m in messages:
            content = re.sub(r"\d{6,}", "***MASKED***", m.get("content", ""))
            masked_messages.append({**m, "content": content})

        try:
            if self.llm is None:
                self._refresh_llm()
            response = self.llm.invoke(masked_messages)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            error_str = str(e)
            if "401" in error_str:
                # Token refresh
                self._refresh_llm()
                response = self.llm.invoke(masked_messages)
                return response.content if hasattr(response, "content") else str(response)
            elif "403" in error_str:
                raise FirewallRejection("403", "Access denied by SafeChain firewall")
            elif "400" in error_str:
                raise FirewallRejection("400", f"Bad request: {error_str}")
            raise

    def _refresh_llm(self) -> None:
        """Refresh the LLM instance from safechain."""
        try:
            from safechain.lcel import model  # type: ignore
            self.llm = model
        except ImportError:
            raise NotImplementedError(
                "SafeChain is not available — cannot refresh LLM."
            )

    @staticmethod
    def _build_tool_schema_block(functions: list[Callable]) -> str:
        """Format tool signatures for prompt injection."""
        lines = ["Available tools (respond with {\"tool_call\": {\"name\": \"...\", \"arguments\": {...}}} to use):"]
        for fn in functions:
            sig = inspect.signature(fn)
            params = []
            for name, param in sig.parameters.items():
                annotation = param.annotation
                type_name = getattr(annotation, "__name__", "string") if annotation != inspect.Parameter.empty else "string"
                default = f" = {param.default}" if param.default is not inspect.Parameter.empty else ""
                params.append(f"{name}: {type_name}{default}")
            doc = (fn.__doc__ or "").strip().split("\n")[0]
            lines.append(f"  - {fn.__name__}({', '.join(params)}): {doc}")
        lines.append("\nWhen done, respond with {\"output\": <your final answer>}.")
        return "\n".join(lines)
