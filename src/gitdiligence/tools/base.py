from abc import ABC, abstractmethod


class Tool(ABC):
    """Classe abstraite que chaque outil doit implémenter."""

    name: str
    description: str
    parameters: dict  # JSON Schema des paramètres attendus par l'outil

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Exécute l'outil avec les paramètres donnés et retourne le résultat en string."""
        ...
