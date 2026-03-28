"""Tests pour les outils GitHub (github_contents.py + search.py).

Ces tests tapent la vraie API GitHub.
Ils sont skippés automatiquement si GITHUB_TOKEN n'est pas défini.
On utilise le repo pallets/flask comme cible — c'est stable et public.
"""

import os
import json
import pytest

from gitdiligence.tools.github_contents import GetRepoInfo, GetFileTree, GetFileContent
from gitdiligence.tools.search import SearchCode

needs_token = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN non défini",
)

OWNER = "pallets"
REPO = "flask"


@needs_token
def test_get_repo_info():
    """Vérifie qu'on récupère les métadonnées d'un repo."""
    tool = GetRepoInfo()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO))

    assert result["name"] == "flask"
    assert result["language"] == "Python"
    assert result["stars"] > 0


@needs_token
def test_get_file_tree():
    """Vérifie qu'on récupère la liste des fichiers d'un repo."""
    tool = GetFileTree()
    result = tool.execute(owner=OWNER, repo=REPO)

    paths = result.split("\n")
    assert len(paths) > 10
    assert any("pyproject.toml" in p for p in paths)


@needs_token
def test_get_file_content():
    """Vérifie qu'on peut lire le contenu d'un fichier."""
    tool = GetFileContent()
    result = tool.execute(owner=OWNER, repo=REPO, path="pyproject.toml")

    assert "Flask" in result
    assert "[project]" in result


@needs_token
def test_search_code():
    """Vérifie que la recherche de code retourne des résultats."""
    tool = SearchCode()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO, query="def create_app"))

    assert len(result) > 0
    assert "path" in result[0]
