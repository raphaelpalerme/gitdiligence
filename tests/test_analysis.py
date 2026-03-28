"""Tests pour les outils d'analyse (dependency.py + security.py).

Pas besoin de token GitHub — ces outils analysent du contenu brut.
"""

import json

from gitdiligence.tools.dependency import AnalyzeDependencies
from gitdiligence.tools.security import CheckSecurity


# --- Tests dependency.py ---


def test_parse_pyproject_toml():
    """Vérifie le parsing d'un pyproject.toml."""
    tool = AnalyzeDependencies()
    content = '[project]\ndependencies = [\n    "flask>=2.0",\n    "requests>=2.28",\n]'
    result = json.loads(tool.execute(filename="pyproject.toml", content=content))

    assert result["count"] == 2
    assert result["dependencies"][0]["name"] == "flask"
    assert result["dependencies"][0]["version"] == ">=2.0"


def test_parse_requirements_txt():
    """Vérifie le parsing d'un requirements.txt."""
    tool = AnalyzeDependencies()
    content = "flask>=2.0\nrequests==2.28.0\n# un commentaire\npydantic"
    result = json.loads(tool.execute(filename="requirements.txt", content=content))

    assert result["count"] == 3
    assert result["dependencies"][2]["name"] == "pydantic"
    assert result["dependencies"][2]["version"] == "non spécifiée"


def test_parse_package_json():
    """Vérifie le parsing d'un package.json."""
    tool = AnalyzeDependencies()
    content = '{"dependencies": {"react": "^18.0"}, "devDependencies": {"jest": "^29.0"}}'
    result = json.loads(tool.execute(filename="package.json", content=content))

    assert result["count"] == 2


def test_unsupported_format():
    """Vérifie qu'un format inconnu retourne une erreur propre."""
    tool = AnalyzeDependencies()
    result = json.loads(tool.execute(filename="Gemfile", content="gem 'rails'"))

    assert "error" in result


# --- Tests security.py ---


def test_security_detects_good_signals():
    """Vérifie la détection des bons signaux (LICENSE, CI, etc.)."""
    tool = CheckSecurity()
    tree = "LICENSE\n.github/workflows/ci.yml\nSECURITY.md"
    result = json.loads(tool.execute(file_tree=tree))

    assert len(result["present"]) >= 3
    assert len(result["warnings"]) == 0


def test_security_detects_warnings():
    """Vérifie la détection des mauvais signaux (.env commité)."""
    tool = CheckSecurity()
    tree = "src/app.py\n.env\nid_rsa"
    result = json.loads(tool.execute(file_tree=tree))

    assert len(result["warnings"]) == 2


def test_security_detects_missing():
    """Vérifie la détection des fichiers manquants."""
    tool = CheckSecurity()
    tree = "src/app.py\nREADME.md"
    result = json.loads(tool.execute(file_tree=tree))

    assert len(result["missing"]) >= 3
