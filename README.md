# GitDiligence

AI-powered technical due diligence for GitHub repositories. Analyzes a repo and produces a structured report scoring 8 dimensions.

## How It Works

GitDiligence uses a ReAct (Reasoning + Acting) agent that:

1. Explores a GitHub repo via the API (metadata, file tree, key files, contributors, activity)
2. Analyzes dependencies, CI/CD, security, documentation
3. Produces a report with 8 dimensions scored 1-10 and a final verdict

The agent is built from scratch (no LangChain), with multi-provider support: **Gemini** (free) and **Claude** (paid, higher quality).

## The 8 Dimensions

| Dimension | What's Evaluated |
|-----------|-----------------|
| Repo Health | Stars, forks, activity, license, bus factor |
| Code Quality | Structure, tests, linter, typing |
| Dependencies | Count, manifests, risky dependencies |
| Contributors | Distribution, recent commits, bus factor |
| Documentation | README, docs/, CONTRIBUTING, CHANGELOG |
| CI/CD & DevOps | CI provider, Docker, IaC |
| Security | SECURITY.md, dependabot, exposed secrets |
| Overall Assessment | Overall score, strengths, risks |

Possible verdicts: `Strong Invest` · `Invest with Caution` · `Pass` · `Needs More Investigation`

## Installation

```bash
git clone https://github.com/raphaelpalerme/gitdiligence.git
cd gitdiligence
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file at the root:

```
GOOGLE_API_KEY=AIza...    # Free — https://aistudio.google.com
GITHUB_TOKEN=ghp_...

# Optional — only for --model claude-sonnet-4-6
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Analyze a repo (Gemini, free)
gitdiligence analyze pallets/flask

# With real-time reasoning
gitdiligence analyze pallets/flask --verbose

# Use Claude (paid, higher quality)
gitdiligence analyze pallets/flask --model claude-sonnet-4-6

# Run evaluation
gitdiligence eval
```

Reports are saved to `./reports/` (Markdown + JSON).

### Free tier limits (Gemini 2.5 Flash)

| Limit | Value |
|-------|-------|
| Requests/day | 20 |
| Requests/min | 5 |

Each analysis uses ~7 requests, so **~2-3 analyses/day** on the free tier. The tool retries automatically on rate limits. For higher throughput, use Claude with `--model claude-sonnet-4-6`.

## Sample Report

<details>
<summary>pallets/flask — 9.1/10, Strong Invest (click to expand)</summary>

| Dimension | Score |
|-----------|-------|
| Repo Health | 10/10 |
| Code Quality | 9/10 |
| Dependencies | 10/10 |
| Contributors | 8/10 |
| Documentation | 10/10 |
| CI/CD & DevOps | 9/10 |
| Security | 8/10 |
| Overall Assessment | 9/10 |

**Key findings:**
- 71k+ stars, 15+ years of active maintenance, backed by the Pallets organization
- 6 runtime dependencies, all from the trusted Pallets ecosystem
- World-class documentation with tutorials, patterns, and deployment guides
- SHA-pinned CI actions, OIDC PyPI publishing, zizmor security scanning
- Bus factor risk: maintenance concentrated on a single active maintainer
- No SECURITY.md or dependabot.yml

**Verdict: Strong Invest** — Flask is a battle-tested, production-grade framework with very low adoption risk.

[Full report](examples/pallets_flask.md)

</details>

## Stack

- **Agent**: ReAct loop from scratch (no LangChain)
- **LLM**: Gemini (free) or Claude (paid), multi-provider with normalized abstraction
- **GitHub**: httpx + GitHub REST API v3
- **Validation**: Pydantic (report + JSON Schema for tools)
- **CLI**: Typer + Rich

## Structure

```
src/gitdiligence/
├── agent/
│   ├── prompts.py          # System prompt
│   ├── state.py            # State management (steps, tokens)
│   └── react.py            # ReAct loop
├── llm/
│   ├── client.py           # Multi-provider dispatcher (Claude + Gemini)
│   └── models.py           # Normalized types (LLMResponse, ToolCall)
├── tools/
│   ├── base.py             # Abstract Tool class
│   ├── registry.py         # Tool registry
│   ├── github_api.py       # GitHub HTTP client
│   ├── github_contents.py  # get_repo_info, get_file_tree, get_file_content
│   ├── github_stats.py     # get_contributors, get_commit_activity, get_languages
│   ├── search.py           # search_code
│   ├── dependency.py       # analyze_dependencies
│   └── security.py         # check_security
├── report/
│   ├── schema.py           # Pydantic report models
│   └── renderer.py         # Markdown renderer
├── eval/
│   ├── fixtures.py         # Reference repos
│   └── runner.py           # Eval runner
├── cli.py                  # CLI (Typer)
└── __main__.py             # python -m gitdiligence
```

## Tests

```bash
pytest -v
```

## License

[MIT](LICENSE)
