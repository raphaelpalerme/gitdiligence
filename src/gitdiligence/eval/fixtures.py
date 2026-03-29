"""Reference repos for evaluation.

Each fixture defines a repo and the expected report outcomes.
"""

from dataclasses import dataclass


@dataclass
class EvalFixture:
    """A test repo with expected results."""

    owner: str
    repo: str
    min_score: float  # Score global minimum attendu
    max_score: float  # Score global maximum attendu
    expected_verdicts: list[str]  # Verdicts acceptables


FIXTURES = [
    EvalFixture(
        owner="pallets",
        repo="flask",
        min_score=7.0,
        max_score=10.0,
        expected_verdicts=["Strong Invest"],
    ),
    EvalFixture(
        owner="kelseyhightower",
        repo="nocode",
        min_score=1.0,
        max_score=5.0,
        expected_verdicts=["Pass", "Needs More Investigation"],
    ),
    EvalFixture(
        owner="pallets",
        repo="click",
        min_score=7.0,
        max_score=10.0,
        expected_verdicts=["Strong Invest", "Invest with Caution"],
    ),
]
