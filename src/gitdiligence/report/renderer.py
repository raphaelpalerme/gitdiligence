"""Rendu Markdown du rapport de due diligence.

Transforme un DiligenceReport (objet Pydantic) en texte Markdown lisible.
"""

from gitdiligence.report.schema import DiligenceReport


def render_markdown(report: DiligenceReport) -> str:
    """Convertit un DiligenceReport en Markdown."""
    lines = []

    # En-tête
    lines.append(f"# Due Diligence: {report.repo_info.owner}/{report.repo_info.name}")
    lines.append("")

    # Métadonnées
    info = report.repo_info
    lines.append("## Repo")
    lines.append(f"- **Description**: {info.description or 'N/A'}")
    lines.append(f"- **Langage**: {info.language or 'N/A'}")
    lines.append(f"- **Stars**: {info.stars:,}")
    lines.append(f"- **Forks**: {info.forks:,}")
    lines.append(f"- **Licence**: {info.license or 'N/A'}")
    lines.append(f"- **Créé le**: {info.created_at}")
    lines.append("")

    # Dimensions
    for dim in report.dimensions:
        lines.append(f"## {dim.name} ({dim.score}/10)")
        lines.append("")
        for finding in dim.findings:
            icon = "+" if finding.positive else "-"
            lines.append(f"  {icon} {finding.detail}")
        lines.append("")
        lines.append(f"**Recommandation**: {dim.recommendation}")
        lines.append("")

    # Score global et verdict
    lines.append("---")
    lines.append(f"## Score global: {report.overall_score}/10")
    lines.append(f"## Verdict: {report.verdict}")
    lines.append("")
    lines.append(report.summary)

    return "\n".join(lines)
