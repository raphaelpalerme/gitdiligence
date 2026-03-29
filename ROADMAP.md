# Roadmap GitDiligence

## V1 — Done

- [x] Project skeleton
- [x] Tool + Registry
- [x] GitHub tools (repo info, file tree, file content, search code)
- [x] Analysis tools (dependencies, security)
- [x] Pydantic schema (8 dimensions)
- [x] LLM client (Claude tool_use)
- [x] System prompt
- [x] State management
- [x] ReAct loop
- [x] Markdown renderer
- [x] CLI (analyze + eval)
- [x] Eval framework
- [x] README
- [x] Gemini support (free, multi-provider)

---

## V1.1 — Polish & completeness

Goal: go from self-analysis score 5/10 to 8+/10 and make the project presentable.

### Missing tools
- [x] `get_contributors` — contributor list + commit counts
- [x] `get_commit_activity` — weekly activity over 1 year
- [x] `get_languages` — language breakdown (% per language)

### Project hygiene
- [x] License (MIT)
- [x] CI/CD — GitHub Actions (tests + ruff lint)
- [x] Dependabot (.github/dependabot.yml)
- [x] SECURITY.md
- [x] CONTRIBUTING.md
- [x] CHANGELOG.md

### Presentation
- [x] Add a sample report (Flask) in the README
- [x] Document Gemini free tier limits in README

---

## V1.2 — CLI & UX + Code quality

Improve the CLI experience before publishing.

- [ ] Progress indicator — show which tool is running (spinner or progress bar)
- [ ] Colored output — green for positive findings, red for negative
- [ ] Summary card at the end — compact score + verdict with Rich panel
- [ ] Error messages — clear, actionable messages for common failures (bad repo, no token, rate limit)
- [ ] `--json` flag — output report as JSON to stdout (for piping)
- [ ] Type annotations — fix Pylance warnings in llm/client.py (strict typing)
### CI & Security hardening
- [ ] SHA-pin GitHub Actions in ci.yml (supply chain security)
- [ ] Add uv.lock for reproducible installs
- [ ] Add mypy or pyright to CI pipeline
- [ ] CI matrix build for Python 3.11 + 3.12
- [ ] Branch protection check in check_security tool

### Project polish
- [ ] Fix GitHub repo description (currently in French)
- [ ] CODE_OF_CONDUCT.md
- [ ] GitHub issue templates (.github/ISSUE_TEMPLATE/)

---

## V1.3 — Robustness

- [ ] Streaming output — show reasoning in real time
- [ ] GitHub API caching — avoid re-reading the same files
- [ ] Support Go (go.mod), Rust (Cargo.toml), Ruby (Gemfile) in dependency.py
- [ ] Truncate large files (> 100KB)

---

## V2 — Features

- [ ] Web UI (Streamlit or FastAPI)
- [ ] Compare mode (2 repos side by side)
- [ ] Vulnerability lookup (OSV.dev API)
- [ ] PDF export
- [ ] Analysis history (SQLite)

