# GitDiligence — Technical Due Diligence Agent

## Context
An autonomous AI agent that analyzes GitHub repos and produces a structured technical due diligence report. A portfolio project to demonstrate mastery of LLM orchestration, the ReAct pattern, and prompt engineering — built from scratch, without LangChain.

---

## Input / Output

- **Input**: GitHub URL or `owner/repo`
- **Output**: Structured report (Markdown + JSON) with scores 1-10 per dimension

---

## Architecture

```
src/gitdiligence/
├── __init__.py
├── __main__.py              # python -m gitdiligence
├── cli.py                   # CLI (typer)
├── agent/
│   ├── react.py             # ReAct loop (core of the project)
│   ├── state.py             # AgentState + Step dataclasses
│   └── prompts.py           # System prompt
├── llm/
│   └── client.py            # Claude API wrapper (messages + tool_use)
├── tools/
│   ├── base.py              # Abstract Tool class
│   ├── registry.py          # ToolRegistry (collection + dispatch)
│   ├── github_api.py        # get_repo_info, get_contributors, get_commit_activity, get_languages
│   ├── github_contents.py   # get_file_tree, get_file_content
│   ├── dependency.py        # parse_dependencies
│   ├── security.py          # check_security_signals
│   └── search.py            # search_code (GitHub code search)
├── report/
│   ├── schema.py            # Pydantic models (DueDiligenceReport)
│   └── renderer.py          # Markdown renderer
└── eval/
    ├── runner.py             # Runs the agent on known repos
    ├── criteria.py           # Scoring (completeness, accuracy, cost)
    └── fixtures/
        └── known_repos.json  # Ground truth for eval
```

---

## ReAct Loop

```
1. Initial message: system prompt + "Analyze repo X"
2. LOOP (max 25 iterations):
   a. Call Claude with messages + tools
   b. Parse response.content:
      - TextBlock → thought (reasoning)
      - ToolUseBlock → tool_name + tool_input
   c. If tool == "generate_report" → validate the report, END
   d. Otherwise → execute the tool, record the Step, append to messages
3. If max reached → force generate_report
4. Return AgentState (steps, report, tokens)
```

**Termination**: the agent calls `generate_report` (a special tool) which validates the report via Pydantic and ends the loop.

---

## 10 Agent Tools

| # | Tool | Description |
|---|------|-------------|
| 1 | `get_repo_info` | Metadata (stars, forks, license, dates, topics) |
| 2 | `get_contributors` | Contributor list + commit counts |
| 3 | `get_commit_activity` | Weekly activity over 1 year |
| 4 | `get_languages` | Language breakdown |
| 5 | `get_file_tree` | Repo file tree (configurable depth) |
| 6 | `get_file_content` | Content of a specific file |
| 7 | `search_code` | Search for patterns in code (GitHub search) |
| 8 | `parse_dependencies` | Manifest analysis (requirements.txt, package.json...) |
| 9 | `check_security_signals` | Committed .env files, SECURITY.md, dependabot, suspicious patterns |
| 10 | `generate_report` | Produces the final report (Pydantic schema = input_schema) |

---

## Report — 8 Dimensions with Score 1-10

1. **Repo Health**: stars, forks, activity, license, bus factor
2. **Code Quality**: languages, structure, tests, linter
3. **Dependencies**: count, manifests, notable dependencies
4. **Contributors**: distribution, recent commits, bus factor
5. **Documentation**: README, docs/, CONTRIBUTING, CHANGELOG
6. **CI/CD & DevOps**: CI provider, Docker, IaC
7. **Security**: policy, dependabot, secrets, .env
8. **Overall Assessment**: overall score, strengths, risks, recommendation

Final recommendation: `Strong Invest` / `Invest with Caution` / `Pass` / `Needs More Investigation`

---

## Tech Stack

```toml
dependencies = [
    "anthropic>=0.86",      # Claude API with native tool_use
    "httpx>=0.28",          # HTTP client for GitHub API
    "pydantic>=2.12",       # Report validation + JSON Schema generation
    "typer>=0.24",          # CLI (type hints, consistent with Pydantic)
    "rich>=14.0",           # Terminal output (progress, markdown)
]
```

Default model: `claude-sonnet-4-6` (configurable via `--model`)

---

## CLI

```bash
gitdiligence analyze <owner/repo>       # Analyze a repo
    --model TEXT                      # LLM model [claude-sonnet-4-6]
    --max-steps INT                   # Max ReAct iterations [25]
    --output-dir PATH                 # Output directory [./reports]
    --format [md|json|both]           # Format [both]
    --verbose                         # Display reasoning in real time

gitdiligence eval                       # Evaluation on known repos
```

---

## Scope V1 (now)

- Complete project skeleton
- 10 functional tools
- ReAct loop with state management
- Pydantic report + Markdown rendering
- `analyze` CLI
- Basic eval (3-5 fixture repos)

## V2 (later)

- Real-time streaming output
- Parallel tool execution
- Vulnerability lookup (OSV.dev API)
- Web UI (Streamlit)
- Comparison mode (2 repos side by side)

---

## Implementation Order

1. Project skeleton (pyproject.toml, .gitignore, .env.example)
2. `tools/base.py` + `tools/registry.py`
3. GitHub tools (`github_api.py`, `github_contents.py`, `search.py`)
4. Remaining tools (`dependency.py`, `security.py`)
5. `report/schema.py` (Pydantic models)
6. `llm/client.py`
7. `agent/prompts.py`
8. `agent/state.py`
9. `agent/react.py` (core of the project)
10. `report/renderer.py`
11. `generate_report` tool (plugs in the Pydantic schema)
12. `cli.py` + `__main__.py`
13. Eval framework
14. CLAUDE.md + README

## Verification

```bash
# Install the project
pip install -e ".[dev]"

# Run an analysis
export ANTHROPIC_API_KEY=sk-...
export GITHUB_TOKEN=ghp_...
gitdiligence analyze anthropics/anthropic-sdk-python --verbose

# Run tests
pytest tests/

# Run eval
gitdiligence eval
```
