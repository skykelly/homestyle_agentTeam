"""
Base workflow class with the agentic loop (tool-use pattern).
"""

import json
from typing import Any
import anthropic

from config.settings import settings
from tools.definitions import TOOLS
from tools.handlers import dispatch


class BaseWorkflow:
    """
    Wraps the Anthropic agentic loop.
    Subclasses define a system prompt and optionally restrict the tool set.
    """

    system_prompt: str = "당신은 한국 퍼포먼스 마케팅 전문가입니다."
    allowed_tools: list[str] | None = None  # None = all tools

    def __init__(self, verbose: bool = True):
        if settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            self.client = anthropic.Anthropic(auth_token=settings.ANTHROPIC_AUTH_TOKEN)
        self.verbose = verbose
        self._tools = (
            [t for t in TOOLS if t["name"] in self.allowed_tools]
            if self.allowed_tools
            else TOOLS
        )

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def run(self, user_message: str, max_iterations: int = 10) -> str:
        """
        Execute the agentic loop until the model stops using tools.
        Returns the final text response.
        """
        messages: list[dict] = [{"role": "user", "content": user_message}]

        for iteration in range(max_iterations):
            response = self.client.messages.create(
                model=settings.MODEL,
                max_tokens=8096,
                system=self.system_prompt,
                tools=self._tools,
                messages=messages,
            )

            self._log(f"\n[Iteration {iteration + 1}] stop_reason={response.stop_reason}")

            # Collect all text blocks for display
            text_parts = [b.text for b in response.content if b.type == "text"]
            if text_parts and self.verbose:
                self._log("\n".join(text_parts))

            if response.stop_reason == "end_turn":
                return "\n".join(text_parts)

            if response.stop_reason == "tool_use":
                # Append assistant message
                messages.append({"role": "assistant", "content": response.content})

                # Process every tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        self._log(f"  -> Tool call: {block.name}({json.dumps(block.input, ensure_ascii=False)[:120]}...)")
                        result_str = dispatch(block.name, block.input)
                        self._log(f"  <- Result preview: {result_str[:200]}...")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str,
                        })

                messages.append({"role": "user", "content": tool_results})
                continue

            # Unexpected stop reason
            break

        # Return whatever text we have
        return "\n".join(
            b.text for b in response.content if hasattr(b, "text") and b.text
        )
