"""Markdown renderer for the due diligence report."""

from gitdiligence.report.schema import DiligenceReport


def render_markdown(report: DiligenceReport) -> str:
    """Convert a DiligenceReport to Markdown."""
    lines = []

    # Header
    lines.append(f"# Due Diligence: {report.repo_info.owner}/{report.repo_info.name}")
    lines.append("")

    info = report.repo_info
    lines.append("## Repo")
    lines.append(f"- **Description**: {info.description or 'N/A'}")
    lines.append(f"- **Language**: {info.language or 'N/A'}")
    lines.append(f"- **Stars**: {info.stars:,}")
    lines.append(f"- **Forks**: {info.forks:,}")
    lines.append(f"- **License**: {info.license or 'N/A'}")
    lines.append(f"- **Created**: {info.created_at}")
    lines.append("")

    for dim in report.dimensions:
        lines.append(f"## {dim.name} ({dim.score}/10)")
        lines.append("")
        for finding in dim.findings:
            icon = "+" if finding.positive else "-"
            lines.append(f"  {icon} {finding.detail}")
        lines.append("")
        lines.append(f"**Recommendation**: {dim.recommendation}")
        lines.append("")

    lines.append("---")
    lines.append(f"## Overall Score: {report.overall_score}/10")
    lines.append(f"## Verdict: {report.verdict}")
    lines.append("")
    lines.append(report.summary)

    return "\n".join(lines)
