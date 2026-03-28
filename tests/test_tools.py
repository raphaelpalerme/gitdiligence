"""Tests pour le système d'outils (base.py + registry.py).

On utilise un FakeTool pour tester le registre sans dépendre
d'un vrai outil (qui n'existe pas encore).
"""

from gitdiligence.tools.base import Tool
from gitdiligence.tools import registry


class FakeTool(Tool):
    """Faux outil qui retourne simplement les paramètres reçus."""

    name = "fake_tool"
    description = "Un outil bidon pour tester"
    parameters = {"type": "object", "properties": {"msg": {"type": "string"}}}

    def execute(self, **kwargs) -> str:
        return f"Reçu: {kwargs}"


def test_register_and_get_tool():
    """Vérifie qu'on peut enregistrer un outil et le retrouver par son nom."""
    tool = FakeTool()
    registry.register(tool)

    assert registry.get_tool("fake_tool").name == "fake_tool"


def test_all_tools():
    """Vérifie que all_tools() retourne bien les outils enregistrés."""
    assert len(registry.all_tools()) >= 1
    names = [t.name for t in registry.all_tools()]
    assert "fake_tool" in names


def test_execute():
    """Vérifie que l'exécution d'un outil via le registre fonctionne."""
    result = registry.get_tool("fake_tool").execute(msg="hello")
    assert result == "Reçu: {'msg': 'hello'}"
