"""GitHub statistics tools (contributors, commit activity, languages).

These tools provide data for the Contributors and Repo Health dimensions
that were previously evaluated blind.
"""

import json

from gitdiligence.tools.base import Tool
from gitdiligence.tools.github_api import github_get


class GetContributors(Tool):
    """Fetches the top contributors of a GitHub repo."""

    name = "get_contributors"
    description = "Get the top contributors of a repo with their commit counts"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"},
        },
        "required": ["owner", "repo"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        data = github_get(f"/repos/{owner}/{repo}/contributors?per_page=20")

        contributors = []
        for c in data:
            contributors.append({
                "login": c["login"],
                "contributions": c["contributions"],
            })

        return json.dumps({
            "total_shown": len(contributors),
            "contributors": contributors,
        }, indent=2)


class GetCommitActivity(Tool):
    """Fetches weekly commit activity over the last year."""

    name = "get_commit_activity"
    description = "Get weekly commit counts over the last year"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"},
        },
        "required": ["owner", "repo"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        data = github_get(f"/repos/{owner}/{repo}/stats/commit_activity")

        # The API may return empty data (202 Accepted = still computing)
        if not data or not isinstance(data, list):
            return json.dumps({"error": "No activity data available (GitHub may still be computing)"})

        total_commits = sum(week["total"] for week in data)
        active_weeks = sum(1 for week in data if week["total"] > 0)
        recent_4_weeks = sum(week["total"] for week in data[-4:])
        recent_12_weeks = sum(week["total"] for week in data[-12:])

        return json.dumps({
            "total_commits_last_year": total_commits,
            "active_weeks": active_weeks,
            "total_weeks": len(data),
            "commits_last_4_weeks": recent_4_weeks,
            "commits_last_12_weeks": recent_12_weeks,
        }, indent=2)


class GetLanguages(Tool):
    """Fetches the language breakdown of a repo."""

    name = "get_languages"
    description = "Get the language breakdown of a repo (percentage per language)"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"},
        },
        "required": ["owner", "repo"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        data = github_get(f"/repos/{owner}/{repo}/languages")

        # API returns {language: bytes}. Convert to percentages.
        total_bytes = sum(data.values()) if data else 0
        if total_bytes == 0:
            return json.dumps({"languages": []})

        languages = []
        for lang, bytes_count in data.items():
            languages.append({
                "language": lang,
                "percentage": round(bytes_count / total_bytes * 100, 1),
                "bytes": bytes_count,
            })

        # Sort by percentage descending
        languages.sort(key=lambda x: x["percentage"], reverse=True)

        return json.dumps({"languages": languages}, indent=2)
