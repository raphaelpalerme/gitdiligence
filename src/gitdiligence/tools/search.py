"""Outil de recherche de code dans un repo GitHub.

Utilise l'API GitHub Search qui cherche dans le code indexé.
Limitation : seule la branche par défaut est indexée.
"""

import json

from gitdiligence.tools.base import Tool
from gitdiligence.tools.github_api import github_get


class SearchCode(Tool):
    """Cherche un mot-clé dans le code d'un repo GitHub."""

    name = "search_code"
    description = "Cherche un mot-clé dans le code d'un repo GitHub"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Propriétaire du repo"},
            "repo": {"type": "string", "description": "Nom du repo"},
            "query": {"type": "string", "description": "Mot-clé à chercher"},
        },
        "required": ["owner", "repo", "query"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        query = kwargs["query"]

        # L'API Search a sa propre syntaxe : "query repo:owner/repo"
        data = github_get(f"/search/code?q={query}+repo:{owner}/{repo}")

        results = []
        for item in data.get("items", [])[:10]:  # Max 10 résultats
            results.append({
                "path": item["path"],
                "url": item["html_url"],
            })
        return json.dumps(results, indent=2)
