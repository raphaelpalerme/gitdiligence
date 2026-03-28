"""Tests pour le system prompt (agent/prompts.py)."""

from gitdiligence.agent.prompts import build_system_prompt


def test_prompt_contains_repo_name():
    """Vérifie que le prompt inclut le owner/repo."""
    prompt = build_system_prompt("pallets", "flask")
    assert "pallets/flask" in prompt


def test_prompt_contains_dimensions():
    """Vérifie que les 8 dimensions sont mentionnées."""
    prompt = build_system_prompt("owner", "repo")
    dimensions = [
        "Repo Health",
        "Code Quality",
        "Dependencies",
        "Contributors",
        "Documentation",
        "CI/CD & DevOps",
        "Security",
        "Overall Assessment",
    ]
    for dim in dimensions:
        assert dim in prompt


def test_prompt_contains_verdicts():
    """Vérifie que les 4 verdicts sont mentionnés."""
    prompt = build_system_prompt("owner", "repo")
    assert "Strong Invest" in prompt
    assert "Pass" in prompt
