"""Tests for the GitHub tools (github_contents.py + search.py).

These tests hit the real GitHub API.
They are automatically skipped if GITHUB_TOKEN is not set.
We use the pallets/flask repo as target — it's stable and public.
"""

import os
import json
import pytest

from gitdiligence.tools.github_contents import GetRepoInfo, GetFileTree, GetFileContent
from gitdiligence.tools.search import SearchCode

needs_token = pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"),
    reason="GITHUB_TOKEN not set",
)

OWNER = "pallets"
REPO = "flask"


@needs_token
def test_get_repo_info():
    """Verify that we retrieve the metadata of a repo."""
    tool = GetRepoInfo()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO))

    assert result["name"] == "flask"
    assert result["language"] == "Python"
    assert result["stars"] > 0


@needs_token
def test_get_file_tree():
    """Verify that we retrieve the file list of a repo."""
    tool = GetFileTree()
    result = tool.execute(owner=OWNER, repo=REPO)

    paths = result.split("\n")
    assert len(paths) > 10
    assert any("pyproject.toml" in p for p in paths)


@needs_token
def test_get_file_content():
    """Verify that we can read the content of a file."""
    tool = GetFileContent()
    result = tool.execute(owner=OWNER, repo=REPO, path="pyproject.toml")

    assert "Flask" in result
    assert "[project]" in result


@needs_token
def test_search_code():
    """Verify that code search returns results."""
    tool = SearchCode()
    result = json.loads(tool.execute(owner=OWNER, repo=REPO, query="def create_app"))

    assert len(result) > 0
    assert "path" in result[0]
