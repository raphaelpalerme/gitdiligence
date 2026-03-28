"""Tests pour le client LLM (llm/client.py).

On teste la conversion Tool → format Claude.
On ne teste pas l'appel API réel (ça coûte des tokens).
"""

from gitdiligence.tools.base import Tool
from gitdiligence.llm.client import tools_to_claude_format


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


def test_tools_to_claude_format():
    """Vérifie que la conversion produit le format attendu par l'API Claude."""
    result = tools_to_claude_format([FakeTool()])

    assert len(result) == 1
    assert result[0]["name"] == "fake"
    assert result[0]["description"] == "Un faux outil"
    assert result[0]["input_schema"]["type"] == "object"
    assert "msg" in result[0]["input_schema"]["properties"]


def test_multiple_tools_conversion():
    """Vérifie que plusieurs outils sont convertis correctement."""
    result = tools_to_claude_format([FakeTool(), FakeTool()])
    assert len(result) == 2
