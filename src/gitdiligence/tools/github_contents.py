"""Outils pour récupérer le contenu d'un repo GitHub.

Trois outils :
- get_repo_info : métadonnées du repo (stars, langage, description...)
- get_file_tree : arborescence des fichiers
- get_file_content : contenu d'un fichier spécifique
"""

import json
import base64

from gitdiligence.tools.base import Tool
from gitdiligence.tools.github_api import github_get


class GetRepoInfo(Tool):
    """Récupère les métadonnées d'un repo GitHub."""

    name = "get_repo_info"
    description = "Récupère les métadonnées d'un repo GitHub (stars, langage, description, etc.)"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Propriétaire du repo"},
            "repo": {"type": "string", "description": "Nom du repo"},
        },
        "required": ["owner", "repo"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        data = github_get(f"/repos/{owner}/{repo}")

        # On extrait seulement les champs utiles pour l'agent
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
    """Récupère l'arborescence des fichiers d'un repo."""

    name = "get_file_tree"
    description = "Récupère l'arborescence des fichiers d'un repo GitHub"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Propriétaire du repo"},
            "repo": {"type": "string", "description": "Nom du repo"},
        },
        "required": ["owner", "repo"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        data = github_get(f"/repos/{owner}/{repo}/git/trees/HEAD?recursive=1")

        # On ne garde que les chemins des fichiers (pas les dossiers)
        paths = [item["path"] for item in data["tree"] if item["type"] == "blob"]

        # Tronque si trop de fichiers (évite d'exploser les tokens)
        max_files = 500
        if len(paths) > max_files:
            truncated = paths[:max_files]
            return "\n".join(truncated) + f"\n\n... ({len(paths)} fichiers au total, tronqué à {max_files})"
        return "\n".join(paths)


class GetFileContent(Tool):
    """Récupère le contenu d'un fichier dans un repo GitHub."""

    name = "get_file_content"
    description = "Récupère le contenu d'un fichier dans un repo GitHub"
    parameters = {
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Propriétaire du repo"},
            "repo": {"type": "string", "description": "Nom du repo"},
            "path": {"type": "string", "description": "Chemin du fichier dans le repo"},
        },
        "required": ["owner", "repo", "path"],
    }

    def execute(self, **kwargs) -> str:
        owner = kwargs["owner"]
        repo = kwargs["repo"]
        path = kwargs["path"]
        data = github_get(f"/repos/{owner}/{repo}/contents/{path}")

        # L'API GitHub retourne le contenu encodé en base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
