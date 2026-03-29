"""Tests for the system prompt (agent/prompts.py)."""

from gitdiligence.agent.prompts import build_system_prompt


def test_prompt_contains_repo_name():
    """Verify that the prompt includes the owner/repo."""
    prompt = build_system_prompt("pallets", "flask")
    assert "pallets/flask" in prompt


def test_prompt_contains_dimensions():
    """Verify that the 8 dimensions are mentioned."""
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
    """Verify that the 4 verdicts are mentioned."""
    prompt = build_system_prompt("owner", "repo")
    assert "Strong Invest" in prompt
    assert "Pass" in prompt
