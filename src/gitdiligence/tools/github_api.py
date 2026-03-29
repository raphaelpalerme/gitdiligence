"""Shared HTTP client for the GitHub API.

All GitHub requests go through this module.
Handles authentication, base URL, and errors.
"""

import os

import httpx

BASE_URL = "https://api.github.com"


def get_client() -> httpx.Client:
    """Create an HTTP client configured for the GitHub API."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=BASE_URL, headers=headers, timeout=30)


def github_get(path: str) -> dict:
    """Make a GET request to the GitHub API and return the JSON response.

    Raises an exception with a clear message if the request fails.
    """
    with get_client() as client:
        response = client.get(path)

        if response.status_code == 404:
            raise ValueError(f"Resource not found: {path}")
        if response.status_code == 403:
            raise ValueError(f"Access denied (rate limit?): {path}")
        response.raise_for_status()

        return response.json()
