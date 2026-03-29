"""Tests for the tool system (base.py + registry.py).

We use a FakeTool to test the registry without depending
on a real tool (which doesn't exist yet).
"""

from gitdiligence.tools.base import Tool
from gitdiligence.tools import registry


class FakeTool(Tool):
    """Fake tool that simply returns the received parameters."""

    name = "fake_tool"
    description = "A dummy tool for testing"
    parameters = {"type": "object", "properties": {"msg": {"type": "string"}}}

    def execute(self, **kwargs) -> str:
        return f"Reçu: {kwargs}"


def test_register_and_get_tool():
    """Verify that we can register a tool and retrieve it by name."""
    tool = FakeTool()
    registry.register(tool)

    assert registry.get_tool("fake_tool").name == "fake_tool"


def test_all_tools():
    """Verify that all_tools() returns the registered tools."""
    assert len(registry.all_tools()) >= 1
    names = [t.name for t in registry.all_tools()]
    assert "fake_tool" in names


def test_execute():
    """Verify that executing a tool via the registry works."""
    result = registry.get_tool("fake_tool").execute(msg="hello")
    assert result == "Reçu: {'msg': 'hello'}"
