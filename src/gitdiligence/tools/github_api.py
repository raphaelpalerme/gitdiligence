"""Client HTTP partagé pour l'API GitHub.

Toutes les requêtes GitHub passent par ce module.
Il gère l'authentification, l'URL de base, et les erreurs.
"""

import os

import httpx

BASE_URL = "https://api.github.com"


def get_client() -> httpx.Client:
    """Crée un client HTTP configuré pour l'API GitHub."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=BASE_URL, headers=headers, timeout=30)


def github_get(path: str) -> dict:
    """Fait un GET sur l'API GitHub et retourne le JSON.

    Lève une exception avec un message clair si la requête échoue.
    """
    with get_client() as client:
        response = client.get(path)

        if response.status_code == 404:
            raise ValueError(f"Ressource introuvable : {path}")
        if response.status_code == 403:
            raise ValueError(f"Accès refusé (rate limit ?) : {path}")
        response.raise_for_status()

        return response.json()
