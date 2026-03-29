"""Tests for analysis tools (dependency.py + security.py).

No GitHub token needed — these tools analyze raw content.
"""

import json

from gitdiligence.tools.dependency import AnalyzeDependencies
from gitdiligence.tools.security import CheckSecurity


# --- Tests dependency.py ---


def test_parse_pyproject_toml():
    """Verify parsing of a pyproject.toml."""
    tool = AnalyzeDependencies()
    content = '[project]\ndependencies = [\n    "flask>=2.0",\n    "requests>=2.28",\n]'
    result = json.loads(tool.execute(filename="pyproject.toml", content=content))

    assert result["count"] == 2
    assert result["dependencies"][0]["name"] == "flask"
    assert result["dependencies"][0]["version"] == ">=2.0"


def test_parse_requirements_txt():
    """Verify parsing of a requirements.txt."""
    tool = AnalyzeDependencies()
    content = "flask>=2.0\nrequests==2.28.0\n# a comment\npydantic"
    result = json.loads(tool.execute(filename="requirements.txt", content=content))

    assert result["count"] == 3
    assert result["dependencies"][2]["name"] == "pydantic"
    assert result["dependencies"][2]["version"] == "unspecified"


def test_parse_package_json():
    """Verify parsing of a package.json."""
    tool = AnalyzeDependencies()
    content = '{"dependencies": {"react": "^18.0"}, "devDependencies": {"jest": "^29.0"}}'
    result = json.loads(tool.execute(filename="package.json", content=content))

    assert result["count"] == 2


def test_unsupported_format():
    """Verify that an unknown format returns a proper error."""
    tool = AnalyzeDependencies()
    result = json.loads(tool.execute(filename="Gemfile", content="gem 'rails'"))

    assert "error" in result


# --- Tests security.py ---


def test_security_detects_good_signals():
    """Verify detection of good signals (LICENSE, CI, etc.)."""
    tool = CheckSecurity()
    tree = "LICENSE\n.github/workflows/ci.yml\nSECURITY.md"
    result = json.loads(tool.execute(file_tree=tree))

    assert len(result["present"]) >= 3
    assert len(result["warnings"]) == 0


def test_security_detects_warnings():
    """Verify detection of bad signals (committed .env)."""
    tool = CheckSecurity()
    tree = "src/app.py\n.env\nid_rsa"
    result = json.loads(tool.execute(file_tree=tree))

    assert len(result["warnings"]) == 2


def test_security_detects_missing():
    """Verify detection of missing files."""
    tool = CheckSecurity()
    tree = "src/app.py\nREADME.md"
    result = json.loads(tool.execute(file_tree=tree))

    assert len(result["missing"]) >= 3
