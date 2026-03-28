"""CLI pour GitDiligence.

Commandes :
- analyze <owner/repo> : lance une analyse de due diligence
- eval : lance l'évaluation sur les repos de référence
"""

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from gitdiligence.agent.react import run_agent
from gitdiligence.report.renderer import render_markdown

app = typer.Typer(help="Agent IA de due diligence technique pour repos GitHub")
console = Console()


def _load_env():
    """Charge le .env s'il existe."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@app.command()
def analyze(
    repo: str = typer.Argument(help="Repo à analyser (format: owner/repo)"),
    model: str = typer.Option("claude-sonnet-4-6", help="Modèle Claude à utiliser"),
    max_steps: int = typer.Option(25, help="Nombre max d'itérations ReAct"),
    output_dir: str = typer.Option("./reports", help="Dossier de sortie"),
    verbose: bool = typer.Option(False, help="Affiche le raisonnement en temps réel"),
):
    """Analyse un repo GitHub et génère un rapport de due diligence."""
    _load_env()

    # Vérifie le format owner/repo
    if "/" not in repo:
        console.print("[red]Format invalide. Utilise : owner/repo[/red]")
        raise typer.Exit(1)

    owner, repo_name = repo.split("/", 1)

    # Vérifie les clés API
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY manquant. Ajoute-le dans .env[/red]")
        raise typer.Exit(1)
    if not os.environ.get("GITHUB_TOKEN"):
        console.print("[red]GITHUB_TOKEN manquant. Ajoute-le dans .env[/red]")
        raise typer.Exit(1)

    console.print(f"Analyse de [bold]{owner}/{repo_name}[/bold] en cours...\n")

    # Lance l'agent
    state = run_agent(
        owner=owner,
        repo=repo_name,
        model=model,
        max_steps=max_steps,
        verbose=verbose,
    )

    # Vérifie qu'on a un rapport
    if state.report is None:
        console.print("[red]L'agent n'a pas produit de rapport.[/red]")
        console.print(f"Étapes effectuées : {len(state.steps)}")
        raise typer.Exit(1)

    # Rendu Markdown
    md = render_markdown(state.report)

    # Sauvegarde
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    md_path = out / f"{owner}_{repo_name}.md"
    md_path.write_text(md)

    json_path = out / f"{owner}_{repo_name}.json"
    json_path.write_text(state.report.model_dump_json(indent=2))

    # Affichage
    console.print(Markdown(md))
    console.print(f"\n[dim]Tokens: {state.total_tokens:,} | Étapes: {len(state.steps)}[/dim]")
    console.print(f"[dim]Rapport sauvegardé: {md_path} + {json_path}[/dim]")


@app.command()
def eval(
    model: str = typer.Option("claude-sonnet-4-6", help="Modèle Claude à utiliser"),
):
    """Lance l'évaluation sur les repos de référence."""
    _load_env()

    from gitdiligence.eval.runner import run_eval

    results = run_eval(model=model)
    failed = [r for r in results if not r.passed]
    if failed:
        raise typer.Exit(1)


def main():
    app()
