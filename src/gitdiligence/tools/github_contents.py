"""GitHub content tools (repo info, file tree, file content)."""

import json
import base64

from gitdiligence.tools.base import Tool
from gitdiligence.tools.github_api import github_get


class GetRepoInfo(Tool):
    """Fetch metadata of a GitHub repo."""

    name = "get_repo_info"
    description = "Get metadata of a GitHub repo (stars, language, description, etc.)"
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
        data = github_get(f"/repos/{owner}/{repo}")

        # Extract only the fields useful for the agent
        info = {
            "name": data["name"],
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "open_issues": data["open_issues_count"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
            "default_branch": data["default_branch"],
            "topics": data.get("topics", []),
        }
        return json.dumps(info, indent=2)


class GetFileTree(Tool):
    """Fetch the file tree of a GitHub repo."""

    name = "get_file_tree"
    description = "Get the file tree of a GitHub repo"
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
        data = github_get(f"/repos/{owner}/{repo}/git/trees/HEAD?recursive=1")

        # Keep only file paths (not directories)
        paths = [item["path"] for item in data["tree"] if item["type"] == "blob"]

        # Truncate if too many files (avoids blowing up tokens)
        max_files = 500
        if len(paths) > max_files:
            truncated = paths[:max_files]
            return "\n".join(truncated) + f"\n\n... ({len(paths)} files total, truncated to {max_files})"
        return "\n".join(paths)


class GetFileContent(Tool):
    """Fetch the content of a file in a GitHub repo."""

    name = "get_file_content"
    description = "Get the content of a file in a GitHub repo"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"},
            "path": {"type": "string", "description": "File path in the repo"},
        },
        "required": ["owner", "repo", "path"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        path = kwargs["path"]
        data = github_get(f"/repos/{owner}/{repo}/contents/{path}")

        # GitHub API returns content encoded in base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
