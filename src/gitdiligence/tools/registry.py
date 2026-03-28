from gitdiligence.tools.base import Tool

_registry: dict[str, Tool] = {}


def register(tool: Tool) -> None:
    """Enregistre un outil dans le registre."""
    _registry[tool.name] = tool


def get_tool(name: str) -> Tool:
    """Récupère un outil par son nom. Lève KeyError si introuvable."""
    return _registry[name]


def all_tools() -> list[Tool]:
    """Retourne la liste de tous les outils enregistrés."""
    return list(_registry.values())
