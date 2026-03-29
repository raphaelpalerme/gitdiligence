from gitdiligence.tools.base import Tool

_registry: dict[str, Tool] = {}


def register(tool: Tool) -> None:
    """Register a tool in the registry."""
    _registry[tool.name] = tool


def get_tool(name: str) -> Tool:
    """Get a tool by name. Raises KeyError if not found."""
    return _registry[name]


def all_tools() -> list[Tool]:
    """Return all registered tools."""
    return list(_registry.values())
