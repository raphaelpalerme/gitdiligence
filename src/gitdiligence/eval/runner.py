"""Run evaluation on reference repos.

For each fixture, run the agent and verify the report
matches expectations (score, verdict, completeness).
"""

from dataclasses import dataclass

from gitdiligence.agent.react import run_agent
from gitdiligence.eval.fixtures import EvalFixture, FIXTURES


@dataclass
class EvalResult:
    """Result of evaluating a single repo."""

    fixture: EvalFixture
    passed: bool
    score: float | None = None
    verdict: str | None = None
    tokens: int = 0
    steps: int = 0
    errors: list[str] | None = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


def evaluate_one(fixture: EvalFixture, model: str = "claude-sonnet-4-6") -> EvalResult:
    """Evaluate the agent on a repo and check expectations."""
    errors = []

    try:
        state = run_agent(
            owner=fixture.owner,
            repo=fixture.repo,
            model=model,
        )
    except Exception as e:
        return EvalResult(
            fixture=fixture,
            passed=False,
            errors=[f"Agent crashed: {e}"],
        )

    if state.report is None:
        return EvalResult(
            fixture=fixture,
            passed=False,
            tokens=state.total_tokens,
            steps=len(state.steps),
            errors=["Agent did not produce a report"],
        )

    report = state.report

    # Check completeness (8 dimensions)
    if len(report.dimensions) != 8:
        errors.append(f"Expected 8 dimensions, got {len(report.dimensions)}")

    # Check score range
    if not (fixture.min_score <= report.overall_score <= fixture.max_score):
        errors.append(
            f"Score {report.overall_score} out of range "
            f"[{fixture.min_score}, {fixture.max_score}]"
        )

    # Check verdict
    if report.verdict not in fixture.expected_verdicts:
        errors.append(
            f"Verdict '{report.verdict}' unexpected, "
            f"expected: {fixture.expected_verdicts}"
        )

    return EvalResult(
        fixture=fixture,
        passed=len(errors) == 0,
        score=report.overall_score,
        verdict=report.verdict,
        tokens=state.total_tokens,
        steps=len(state.steps),
        errors=errors,
    )


def run_eval(model: str = "claude-sonnet-4-6") -> list[EvalResult]:
    """Run evaluation on all fixtures."""
    results = []
    for fixture in FIXTURES:
        print(f"\nEval: {fixture.owner}/{fixture.repo}...")
        result = evaluate_one(fixture, model=model)

        status = "PASS" if result.passed else "FAIL"
        print(f"  {status} — score={result.score}, verdict={result.verdict}, "
              f"tokens={result.tokens:,}, steps={result.steps}")
        if result.errors:
            for err in result.errors:
                print(f"  ERROR: {err}")

        results.append(result)

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    total_tokens = sum(r.tokens for r in results)
    print(f"\n{'='*40}")
    print(f"Result: {passed}/{total} passed, {total_tokens:,} tokens total")

    return results
