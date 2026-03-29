"""Tests for the Markdown rendering (report/renderer.py)."""

from gitdiligence.report.schema import DiligenceReport, Dimension, Finding, RepoInfo
from gitdiligence.report.renderer import render_markdown


def _make_report():
    """Create a test report."""
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
                    Finding(detail="Good point", positive=True),
                    Finding(detail="Weakness", positive=False),
                ],
                recommendation="Conseil utile",
            )
            for i in range(8)
        ],
        overall_score=8.0,
        verdict="Strong Invest",
        summary="Excellent project.",
    )


def test_render_contains_header():
    """The Markdown contains the title with owner/repo."""
    md = render_markdown(_make_report())
    assert "# Due Diligence: pallets/flask" in md


def test_render_contains_dimensions():
    """The Markdown contains the dimensions with their score."""
    md = render_markdown(_make_report())
    assert "(8/10)" in md


def test_render_contains_findings():
    """The Markdown contains the findings with + and -."""
    md = render_markdown(_make_report())
    assert "+ Good point" in md
    assert "- Weakness" in md


def test_render_contains_verdict():
    """The Markdown contains the final verdict."""
    md = render_markdown(_make_report())
    assert "Strong Invest" in md
    assert "Excellent project." in md
