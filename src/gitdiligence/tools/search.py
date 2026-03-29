"""Code search tool for GitHub repos.

Uses the GitHub Search API (only the default branch is indexed).
"""

import json

from gitdiligence.tools.base import Tool
from gitdiligence.tools.github_api import github_get


class SearchCode(Tool):
    """Search for a keyword in the code of a GitHub repo."""

    name = "search_code"
    description = "Search for a keyword in the code of a GitHub repo"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"},
            "query": {"type": "string", "description": "Keyword to search for"},
        },
        "required": ["owner", "repo", "query"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        query = kwargs["query"]

        # The Search API has its own syntax: "query repo:owner/repo"
        data = github_get(f"/search/code?q={query}+repo:{owner}/{repo}")

        results = []
        for item in data.get("items", [])[:10]:  # Max 10 results
            results.append({
                "path": item["path"],
                "url": item["html_url"],
            })
        return json.dumps(results, indent=2)
