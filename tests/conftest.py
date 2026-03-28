"""Configuration partagée pour les tests.

Charge le fichier .env pour que les tests aient accès
aux variables d'environnement (GITHUB_TOKEN, etc.).
"""

import os
from pathlib import Path


def load_dotenv():
    """Charge les variables du .env dans os.environ."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


# Chargé une seule fois au démarrage de pytest
load_dotenv()
