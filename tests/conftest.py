"""Shared configuration for tests.

Loads the .env file so that tests have access
to environment variables (GITHUB_TOKEN, etc.).
"""

import os
from pathlib import Path


def load_dotenv():
    """Load variables from .env into os.environ."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


# Loaded once at pytest startup
load_dotenv()
