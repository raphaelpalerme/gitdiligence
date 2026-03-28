"""Tests pour le rendu Markdown (report/renderer.py)."""

from gitdiligence.report.schema import DiligenceReport, Dimension, Finding, RepoInfo
from gitdiligence.report.renderer import render_markdown


def _make_report():
    """Crée un rapport de test."""
    return DiligenceReport(
        repo_info=RepoInfo(
            name="flask", owner="pallets", stars=71000, forks=16000,
            created_at="2010-04-06", language="Python", license="BSD-3-Clause",
            description="The Python micro framework",
        ),
        dimensions=[
            Dimension(
                name=f"Dimension {i}",
                score=8,
                findings=[
                    Finding(detail="Bon point", positive=True),
                    Finding(detail="Point faible", positive=False),
                ],
                recommendation="Conseil utile",
            )
            for i in range(8)
        ],
        overall_score=8.0,
        verdict="Strong Invest",
        summary="Excellent projet.",
    )


def test_render_contains_header():
    """Le Markdown contient le titre avec owner/repo."""
    md = render_markdown(_make_report())
    assert "# Due Diligence: pallets/flask" in md


def test_render_contains_dimensions():
    """Le Markdown contient les dimensions avec leur score."""
    md = render_markdown(_make_report())
    assert "(8/10)" in md


def test_render_contains_findings():
    """Le Markdown contient les findings avec + et -."""
    md = render_markdown(_make_report())
    assert "+ Bon point" in md
    assert "- Point faible" in md


def test_render_contains_verdict():
    """Le Markdown contient le verdict final."""
    md = render_markdown(_make_report())
    assert "Strong Invest" in md
    assert "Excellent projet." in md
