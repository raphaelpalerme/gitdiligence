"""Outil d'analyse des signaux de sécurité d'un repo.

Heuristiques simples basées sur la présence/absence de fichiers.
Ce n'est pas un scanner de vulnérabilités — juste des indicateurs rapides.
"""

import json

from gitdiligence.tools.base import Tool


# Fichiers dont la présence est un bon signe
GOOD_SIGNALS = {
    "SECURITY.md": "Politique de sécurité documentée",
    ".github/dependabot.yml": "Mises à jour automatiques des dépendances",
    "Dockerfile": "Containerisation (reproductibilité)",
    ".github/workflows": "CI/CD en place",
    "LICENSE": "Licence définie",
}

# Fichiers dont la présence est un mauvais signe
BAD_SIGNALS = {
    ".env": "Fichier .env commité (secrets potentiellement exposés)",
    "id_rsa": "Clé SSH privée dans le repo",
    ".npmrc": "Config npm potentiellement avec token",
}


class CheckSecurity(Tool):
    """Analyse la liste des fichiers d'un repo pour repérer des signaux de sécurité."""

    name = "check_security"
    description = "Analyse l'arborescence d'un repo pour repérer des signaux de sécurité"
    parameters = {
        "type": "object",
        "properties": {
            "file_tree": {
                "type": "string",
                "description": "Liste des fichiers du repo (un par ligne)",
            },
        },
        "required": ["file_tree"],
    }

    def execute(self, **kwargs) -> str:
        file_tree = kwargs["file_tree"]
        files = set(file_tree.split("\n"))

        present = []
        missing = []
        warnings = []

        # Vérifie les bons signaux
        for pattern, description in GOOD_SIGNALS.items():
            # Cherche si un fichier contient le pattern (pour gérer les sous-dossiers)
            if any(pattern in f for f in files):
                present.append({"file": pattern, "signal": description})
            else:
                missing.append({"file": pattern, "signal": description})

        # Vérifie les mauvais signaux
        for pattern, description in BAD_SIGNALS.items():
            if any(f.endswith(pattern) for f in files):
                warnings.append({"file": pattern, "signal": description})

        return json.dumps(
            {"present": present, "missing": missing, "warnings": warnings},
            indent=2,
        )
