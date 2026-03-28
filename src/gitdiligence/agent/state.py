"""State management de l'agent ReAct.

Garde trace des messages, des étapes (steps), des tokens consommés,
et du rapport final. Utilisé par react.py pendant la boucle.
"""

from dataclasses import dataclass, field

from gitdiligence.report.schema import DiligenceReport


@dataclass
class Step:
    """Une étape de la boucle ReAct (un appel d'outil)."""

    tool_name: str
    tool_input: dict
    result: str
    thought: str = ""  # Le raisonnement de Claude avant l'appel


@dataclass
class AgentState:
    """État complet de l'agent pendant une analyse."""

    owner: str
    repo: str
    messages: list[dict] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    report: DiligenceReport | None = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def is_done(self) -> bool:
        return self.report is not None

    def add_step(self, step: Step) -> None:
        self.steps.append(step)

    def add_tokens(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
