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
- [ ] `get_contributors` — contributor list + commit counts
- [ ] `get_commit_activity` — weekly activity over 1 year
- [ ] `get_languages` — language breakdown (% per language)

### Project hygiene
- [ ] License (MIT)
- [ ] CI/CD — GitHub Actions (tests + ruff lint)
- [ ] Dependabot (.github/dependabot.yml)
- [ ] SECURITY.md
- [ ] CONTRIBUTING.md
- [ ] CHANGELOG.md

### Presentation
- [ ] Switch everything to English (README, code, docstrings, prompts, reports)
- [ ] Add a sample report (Flask) in the README

---

## V1.2 — CLI & UX

Improve the CLI experience before publishing.

- [ ] Progress indicator — show which tool is running (spinner or progress bar)
- [ ] Colored output — green for positive findings, red for negative
- [ ] Summary card at the end — compact score + verdict with Rich panel
- [ ] Error messages — clear, actionable messages for common failures (bad repo, no token, rate limit)
- [ ] `--json` flag — output report as JSON to stdout (for piping)

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

---

## Visibility

- [x] Push to GitHub
- [x] Free Gemini support (PR #1)
- [ ] Publish on Reddit/HackerNews, collect feedback
- [ ] Post on LinkedIn/Twitter with a sample analysis
