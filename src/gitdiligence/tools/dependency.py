"""Outil d'analyse des dépendances d'un projet.

Parse les fichiers de dépendances courants (pyproject.toml, package.json,
requirements.txt) et retourne une liste structurée.
"""

import json
import re

from gitdiligence.tools.base import Tool


def parse_requirements_txt(content: str) -> list[dict]:
    """Parse un fichier requirements.txt."""
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Sépare le nom du package de la version (ex: "flask>=2.0")
        match = re.match(r"^([a-zA-Z0-9_-]+)\s*([><=!~]+.+)?$", line)
        if match:
            deps.append({"name": match.group(1), "version": match.group(2) or "non spécifiée"})
    return deps


def parse_pyproject_toml(content: str) -> list[dict]:
    """Parse les dépendances d'un pyproject.toml (section dependencies)."""
    deps = []
    in_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_deps = True
            continue
        if in_deps:
            if stripped == "]":
                break
            # Extrait "flask>=2.0" depuis '    "flask>=2.0",'
            match = re.match(r'^\s*"([a-zA-Z0-9_-]+)\s*([><=!~]+[^"]*)?",?$', stripped)
            if match:
                deps.append({"name": match.group(1), "version": match.group(2) or "non spécifiée"})
    return deps


def parse_package_json(content: str) -> list[dict]:
    """Parse les dépendances d'un package.json."""
    data = json.loads(content)
    deps = []
    for section in ["dependencies", "devDependencies"]:
        for name, version in data.get(section, {}).items():
            deps.append({"name": name, "version": version})
    return deps


# Associe un nom de fichier à son parser
PARSERS = {
    "requirements.txt": parse_requirements_txt,
    "pyproject.toml": parse_pyproject_toml,
    "package.json": parse_package_json,
}


class AnalyzeDependencies(Tool):
    """Analyse le contenu d'un fichier de dépendances."""

    name = "analyze_dependencies"
    description = "Analyse un fichier de dépendances et retourne la liste structurée des packages"
    parameters = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Nom du fichier (requirements.txt, pyproject.toml, package.json)",
            },
            "content": {
                "type": "string",
                "description": "Contenu brut du fichier",
            },
        },
        "required": ["filename", "content"],
    }

    def execute(self, **kwargs) -> str:
        filename = kwargs["filename"]
        content = kwargs["content"]

        parser = PARSERS.get(filename)
        if not parser:
            return json.dumps({"error": f"Format non supporté : {filename}"})

        deps = parser(content)
        return json.dumps({"filename": filename, "count": len(deps), "dependencies": deps}, indent=2)
