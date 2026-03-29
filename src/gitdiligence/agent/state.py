"""ReAct agent state management.

Tracks messages, steps, token usage, and the final report.
Used by react.py during the agent loop.
"""

from dataclasses import dataclass, field

from gitdiligence.report.schema import DiligenceReport


@dataclass
class Step:
    """A single step in the ReAct loop (one tool call)."""

    tool_name: str
    tool_input: dict
    result: str
    thought: str = ""  # LLM reasoning before the tool call


@dataclass
class AgentState:
    """Full agent state during an analysis."""

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
