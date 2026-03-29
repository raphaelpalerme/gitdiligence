"""Tests for GitHub stats tools (contributors, commit activity, languages).

These tests hit the real GitHub API.
Skipped automatically if GITHUB_TOKEN is not set.
"""

import os
import json
import pytest

from gitdiligence.tools.github_stats import GetContributors, GetCommitActivity, GetLanguages

needs_token = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN not set",
)

OWNER = "pallets"
REPO = "flask"


@needs_token
def test_get_contributors():
    """Verify we get a list of contributors with commit counts."""
    tool = GetContributors()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO))

    assert result["total_shown"] > 0
    assert result["contributors"][0]["login"]
    assert result["contributors"][0]["contributions"] > 0


@needs_token
def test_get_commit_activity():
    """Verify we get commit activity data for the last year."""
    tool = GetCommitActivity()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO))

    assert result["total_commits_last_year"] > 0
    assert result["total_weeks"] == 52
    assert result["active_weeks"] > 0


@needs_token
def test_get_languages():
    """Verify we get a language breakdown with percentages."""
    tool = GetLanguages()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO))

    assert len(result["languages"]) > 0
    assert result["languages"][0]["language"] == "Python"
    assert result["languages"][0]["percentage"] > 50
