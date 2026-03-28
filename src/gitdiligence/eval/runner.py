"""Lance l'évaluation sur les repos de référence.

Pour chaque fixture, lance l'agent et vérifie que le rapport
correspond aux attentes (score, verdict, complétude).
"""

from dataclasses import dataclass

from gitdiligence.agent.react import run_agent
from gitdiligence.eval.fixtures import EvalFixture, FIXTURES


@dataclass
class EvalResult:
    """Résultat de l'évaluation d'un repo."""

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
    """Évalue l'agent sur un repo et vérifie les attentes."""
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
            errors=[f"Crash de l'agent : {e}"],
        )

    # Pas de rapport → échec
    if state.report is None:
        return EvalResult(
            fixture=fixture,
            passed=False,
            tokens=state.total_tokens,
            steps=len(state.steps),
            errors=["L'agent n'a pas produit de rapport"],
        )

    report = state.report

    # Vérifie la complétude (8 dimensions)
    if len(report.dimensions) != 8:
        errors.append(f"Attendu 8 dimensions, obtenu {len(report.dimensions)}")

    # Vérifie le range de score
    if not (fixture.min_score <= report.overall_score <= fixture.max_score):
        errors.append(
            f"Score {report.overall_score} hors range "
            f"[{fixture.min_score}, {fixture.max_score}]"
        )

    # Vérifie le verdict
    if report.verdict not in fixture.expected_verdicts:
        errors.append(
            f"Verdict '{report.verdict}' non attendu, "
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
    """Lance l'évaluation sur toutes les fixtures."""
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

    # Résumé
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    total_tokens = sum(r.tokens for r in results)
    print(f"\n{'='*40}")
    print(f"Résultat: {passed}/{total} passés, {total_tokens:,} tokens total")

    return results
