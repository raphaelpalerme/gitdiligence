"""Tests for the Pydantic models of the report (report/schema.py).

Verify that validation accepts valid data and rejects invalid data.
"""

import pytest
from pydantic import ValidationError

from gitdiligence.report.schema import DiligenceReport, Dimension, Finding, RepoInfo


def _make_dimension(name="Test", score=7):
    """Helper to create a valid dimension."""
    return Dimension(
        name=name,
        score=score,
        findings=[Finding(detail="Observation", positive=True)],
        recommendation="Conseil",
    )


def _make_report(**overrides):
    """Helper to create a valid report with optional overrides."""
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
    """A report with all correct data is accepted."""
    report = _make_report()
    assert report.verdict == "Strong Invest"
    assert len(report.dimensions) == 8


def test_score_must_be_between_1_and_10():
    """A score outside bounds is rejected."""
    with pytest.raises(ValidationError):
        _make_dimension(score=0)
    with pytest.raises(ValidationError):
        _make_dimension(score=11)


def test_report_needs_exactly_8_dimensions():
    """The report must have exactly 8 dimensions."""
    with pytest.raises(ValidationError):
        _make_report(dimensions=[_make_dimension() for _ in range(3)])


def test_json_schema_is_generated():
    """Pydantic generates a JSON Schema usable by the Claude API."""
    schema = DiligenceReport.model_json_schema()
    assert "properties" in schema
    assert "dimensions" in schema["properties"]
