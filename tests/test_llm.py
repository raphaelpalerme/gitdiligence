"""Tests pour le client LLM multi-provider (llm/client.py).

On teste les conversions de format et la détection de provider.
On ne teste pas les appels API réels.
"""

from gitdiligence.tools.base import Tool
from gitdiligence.llm.client import (
    tools_to_claude_format,
    tools_to_gemini_format,
    detect_provider,
    _extra_tools_to_gemini,
)


class FakeTool(Tool):
    name = "fake"
    description = "Un faux outil"
    parameters = {
        "type": "object",
        "properties": {"msg": {"type": "string"}},
        "required": ["msg"],
    }

    def execute(self, **kwargs) -> str:
        return ""


# --- Détection du provider ---


def test_detect_provider_claude():
    """Les modèles Claude sont détectés correctement."""
    assert detect_provider("claude-sonnet-4-6") == "claude"
    assert detect_provider("claude-haiku-4-5") == "claude"
    assert detect_provider("claude-opus-4-6") == "claude"


def test_detect_provider_gemini():
    """Les modèles Gemini sont détectés correctement."""
    assert detect_provider("gemini-2.5-flash") == "gemini"
    assert detect_provider("gemini-2.0-flash") == "gemini"


# --- Format Claude ---


def test_tools_to_claude_format():
    """Vérifie le format Claude (input_schema)."""
    result = tools_to_claude_format([FakeTool()])

    assert len(result) == 1
    assert result[0]["name"] == "fake"
    assert result[0]["input_schema"]["type"] == "object"
    assert "msg" in result[0]["input_schema"]["properties"]


# --- Format Gemini ---


def test_tools_to_gemini_format():
    """Vérifie le format Gemini (parameters au lieu de input_schema)."""
    result = tools_to_gemini_format([FakeTool()])

    assert len(result) == 1
    assert result[0]["name"] == "fake"
    assert result[0]["parameters"]["type"] == "object"
    assert "msg" in result[0]["parameters"]["properties"]


def test_extra_tools_to_gemini():
    """Vérifie la conversion des extra_tools (format Claude → Gemini)."""
    extra = [{"name": "report", "description": "Génère un rapport", "input_schema": {"type": "object"}}]
    result = _extra_tools_to_gemini(extra)

    assert result[0]["name"] == "report"
    assert result[0]["parameters"] == {"type": "object"}
    assert "input_schema" not in result[0]
