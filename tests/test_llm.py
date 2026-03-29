"""Tests for the multi-provider LLM client (llm/client.py).

We test format conversions and provider detection.
We do not test real API calls.
"""

from gitdiligence.tools.base import Tool
from gitdiligence.llm.client import (
    tools_to_claude_format,
    tools_to_gemini_format,
    detect_provider,
    _extra_tools_to_gemini,
    _resolve_refs,
)


class FakeTool(Tool):
    name = "fake"
    description = "A fake tool"
    parameters = {
        "type": "object",
        "properties": {"msg": {"type": "string"}},
        "required": ["msg"],
    }

    def execute(self, **kwargs) -> str:
        return ""


# --- Provider detection ---


def test_detect_provider_claude():
    """Claude models are detected correctly."""
    assert detect_provider("claude-sonnet-4-6") == "claude"
    assert detect_provider("claude-haiku-4-5") == "claude"
    assert detect_provider("claude-opus-4-6") == "claude"


def test_detect_provider_gemini():
    """Gemini models are detected correctly."""
    assert detect_provider("gemini-2.5-flash") == "gemini"
    assert detect_provider("gemini-2.0-flash") == "gemini"


# --- Claude format ---


def test_tools_to_claude_format():
    """Verify the Claude format (input_schema)."""
    result = tools_to_claude_format([FakeTool()])

    assert len(result) == 1
    assert result[0]["name"] == "fake"
    assert result[0]["input_schema"]["type"] == "object"
    assert "msg" in result[0]["input_schema"]["properties"]


# --- Gemini format ---


def test_tools_to_gemini_format():
    """Verify the Gemini format (parameters instead of input_schema)."""
    result = tools_to_gemini_format([FakeTool()])

    assert len(result) == 1
    assert result[0]["name"] == "fake"
    assert result[0]["parameters"]["type"] == "object"
    assert "msg" in result[0]["parameters"]["properties"]


def test_extra_tools_to_gemini():
    """Verify the conversion of extra_tools (Claude format to Gemini)."""
    extra = [{"name": "report", "description": "Generate a report", "input_schema": {"type": "object"}}]
    result = _extra_tools_to_gemini(extra)

    assert result[0]["name"] == "report"
    assert result[0]["parameters"] == {"type": "object"}
    assert "input_schema" not in result[0]


# --- Resolve $refs ---


def test_resolve_refs():
    """Verify that $ref are inlined and $defs removed."""
    schema = {
        "type": "object",
        "properties": {
            "info": {"$ref": "#/$defs/RepoInfo"},
        },
        "$defs": {
            "RepoInfo": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            }
        },
    }
    resolved = _resolve_refs(schema)

    assert "$defs" not in resolved
    assert "$ref" not in resolved["properties"]["info"]
    assert resolved["properties"]["info"]["type"] == "object"
    assert "name" in resolved["properties"]["info"]["properties"]


def test_resolve_refs_no_defs():
    """A schema without $defs is returned as-is."""
    schema = {"type": "object", "properties": {"x": {"type": "string"}}}
    resolved = _resolve_refs(schema)
    assert resolved == {"type": "object", "properties": {"x": {"type": "string"}}}


# --- Multiple tools ---


def test_multiple_tools_claude():
    """Multiple tools are converted correctly for Claude."""
    result = tools_to_claude_format([FakeTool(), FakeTool()])
    assert len(result) == 2


def test_multiple_tools_gemini():
    """Multiple tools are converted correctly for Gemini."""
    result = tools_to_gemini_format([FakeTool(), FakeTool()])
    assert len(result) == 2
