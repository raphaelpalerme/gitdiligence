"""Types normalisés pour supporter plusieurs providers LLM.

Ces dataclasses sont le format commun entre Claude et Gemini.
react.py utilise uniquement ces types, jamais les types natifs des SDKs.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """Un appel d'outil demandé par le LLM."""

    name: str
    input: dict
    id: str  # tool_use_id pour Claude, id synthétique pour Gemini


@dataclass
class Usage:
    """Tokens consommés par un appel LLM."""

    input_tokens: int
    output_tokens: int


@dataclass
class LLMResponse:
    """Réponse normalisée d'un LLM (Claude ou Gemini)."""

    text: str  # Le raisonnement (thought)
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: Usage = field(default_factory=lambda: Usage(0, 0))
    raw_content: Any = None  # Contenu natif du provider (pour l'historique des messages)
    provider: str = ""  # "claude" ou "gemini"
