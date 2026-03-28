"""Tests pour les modèles Pydantic du rapport (report/schema.py).

Vérifie que la validation accepte les bonnes données et rejette les mauvaises.
"""

import pytest
from pydantic import ValidationError

from gitdiligence.report.schema import DiligenceReport, Dimension, Finding, RepoInfo


def _make_dimension(name="Test", score=7):
    """Helper pour créer une dimension valide."""
    return Dimension(
        name=name,
        score=score,
        findings=[Finding(detail="Observation", positive=True)],
        recommendation="Conseil",
    )


def _make_report(**overrides):
    """Helper pour créer un rapport valide avec des overrides possibles."""
    defaults = {
        "repo_info": RepoInfo(
            name="flask", owner="pallets", stars=71000, forks=16000,
            created_at="2010-04-06", language="Python", license="BSD-3-Clause",
        ),
        "dimensions": [_make_dimension(f"Dim {i}") for i in range(8)],
        "overall_score": 7.5,
        "verdict": "Strong Invest",
        "summary": "Bon projet.",
    }
    defaults.update(overrides)
    return DiligenceReport(**defaults)


def test_valid_report():
    """Un rapport avec toutes les données correctes est accepté."""
    report = _make_report()
    assert report.verdict == "Strong Invest"
    assert len(report.dimensions) == 8


def test_score_must_be_between_1_and_10():
    """Un score hors limites est rejeté."""
    with pytest.raises(ValidationError):
        _make_dimension(score=0)
    with pytest.raises(ValidationError):
        _make_dimension(score=11)


def test_report_needs_exactly_8_dimensions():
    """Le rapport doit avoir exactement 8 dimensions."""
    with pytest.raises(ValidationError):
        _make_report(dimensions=[_make_dimension() for _ in range(3)])


def test_json_schema_is_generated():
    """Pydantic génère un JSON Schema utilisable par l'API Claude."""
    schema = DiligenceReport.model_json_schema()
    assert "properties" in schema
    assert "dimensions" in schema["properties"]
