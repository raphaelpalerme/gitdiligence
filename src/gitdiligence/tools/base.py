from abc import ABC, abstractmethod


class Tool(ABC):
    """Abstract base class that every tool must implement."""

    name: str
    description: str
    parameters: dict  # JSON Schema for the tool's expected parameters

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with the given parameters and return the result as a string."""
        ...
