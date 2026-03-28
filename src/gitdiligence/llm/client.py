"""Client pour l'API Claude avec support tool_use.

Ce module fait le pont entre nos outils (Tool) et l'API Anthropic.
Il convertit nos Tool en format Claude et envoie les requêtes.
"""

import os
import time

import anthropic

from gitdiligence.tools.base import Tool


def tools_to_claude_format(tools: list[Tool]) -> list[dict]:
    """Convertit nos outils au format attendu par l'API Claude.

    Claude attend : {"name": ..., "description": ..., "input_schema": ...}
    Notre Tool a : name, description, parameters
    """
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters,
        }
        for tool in tools
    ]


def call_claude(
    messages: list[dict],
    tools: list[Tool],
    system: str,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 16000,
    extra_tools: list[dict] | None = None,
) -> anthropic.types.Message:
    """Appelle l'API Claude avec des messages et des outils.

    extra_tools : outils déjà au format Claude (ex: generate_report).
    Retourne la réponse brute de l'API. C'est la boucle ReAct (react.py)
    qui décidera quoi faire avec.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    all_tools = tools_to_claude_format(tools) + (extra_tools or [])

    # Retry automatique sur rate limit (429)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=all_tools,
            )
            return response
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait = 60 * (attempt + 1)  # 60s, 120s, 180s
            print(f"Rate limit atteint. Attente de {wait}s...")
            time.sleep(wait)
