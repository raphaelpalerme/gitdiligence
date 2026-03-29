"""Normalized types for multi-provider LLM support.

These dataclasses are the common format between Claude and Gemini.
react.py only uses these types, never the native SDK types.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A tool call requested by the LLM."""

    name: str
    input: dict
    id: str  # tool_use_id for Claude, synthetic id for Gemini


@dataclass
class Usage:
    """Tokens consumed by an LLM call."""

    input_tokens: int
    output_tokens: int


@dataclass
class LLMResponse:
    """Normalized LLM response (Claude or Gemini)."""

    text: str  # The reasoning (thought)
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: Usage = field(default_factory=lambda: Usage(0, 0))
    raw_content: Any = None  # Provider-native content (for message history)
    provider: str = ""  # "claude" or "gemini"
