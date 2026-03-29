"""GitDiligence CLI.

Commands:
- analyze <owner/repo>: run a due diligence analysis
- eval: run evaluation on reference repos
"""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from gitdiligence.agent.react import run_agent
from gitdiligence.llm.client import detect_provider
from gitdiligence.report.renderer import render_markdown

app = typer.Typer(help="AI-powered technical due diligence for GitHub repos")
console = Console()


def _load_env():
    """Load .env file if it exists."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@app.command()
def analyze(
    repo: str = typer.Argument(help="Repo to analyze (format: owner/repo)"),
    model: str = typer.Option("gemini-2.5-flash", help="LLM model (gemini-2.5-flash, claude-sonnet-4-6, etc.)"),
    max_steps: int = typer.Option(25, help="Max ReAct iterations"),
    output_dir: str = typer.Option("./reports", help="Output directory"),
    verbose: bool = typer.Option(False, help="Show reasoning in real time"),
):
    """Analyze a GitHub repo and generate a due diligence report."""
    _load_env()

    if "/" not in repo:
        console.print("[red]Invalid format. Use: owner/repo[/red]")
        raise typer.Exit(1)

    owner, repo_name = repo.split("/", 1)

    provider = detect_provider(model)
    if provider == "gemini" and not os.environ.get("GOOGLE_API_KEY"):
        console.print("[red]GOOGLE_API_KEY missing. Add it to .env[/red]")
        raise typer.Exit(1)
    if provider == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY missing. Add it to .env[/red]")
        raise typer.Exit(1)
    if not os.environ.get("GITHUB_TOKEN"):
        console.print("[red]GITHUB_TOKEN missing. Add it to .env[/red]")
        raise typer.Exit(1)

    console.print(f"Analyzing [bold]{owner}/{repo_name}[/bold]...\n")

    # Lance l'agent
    state = run_agent(
        owner=owner,
        repo=repo_name,
        model=model,
        max_steps=max_steps,
        verbose=verbose,
    )

    if state.report is None:
        console.print("[red]The agent did not produce a report.[/red]")
        console.print(f"Steps completed: {len(state.steps)}")
        raise typer.Exit(1)

    md = render_markdown(state.report)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    md_path = out / f"{owner}_{repo_name}.md"
    md_path.write_text(md)

    json_path = out / f"{owner}_{repo_name}.json"
    json_path.write_text(state.report.model_dump_json(indent=2))

    console.print(Markdown(md))
    console.print(f"\n[dim]Tokens: {state.total_tokens:,} | Steps: {len(state.steps)}[/dim]")
    console.print(f"[dim]Report saved: {md_path} + {json_path}[/dim]")


@app.command()
def eval(
    model: str = typer.Option("gemini-2.5-flash", help="LLM model (gemini-2.5-flash, claude-sonnet-4-6, etc.)"),
):
    """Run evaluation on reference repos."""
    _load_env()

    from gitdiligence.eval.runner import run_eval

    results = run_eval(model=model)
    failed = [r for r in results if not r.passed]
    if failed:
        raise typer.Exit(1)


def main():
    app()
