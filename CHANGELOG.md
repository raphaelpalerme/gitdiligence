# Changelog

## [0.2.0] - 2026-03-29

### Added
- Gemini 2.5 Flash as free default LLM backend
- Multi-provider abstraction (Claude + Gemini)
- `get_contributors` tool — contributor list with commit counts
- `get_commit_activity` tool — weekly activity over 1 year
- `get_languages` tool — language breakdown by percentage
- MIT license
- CI/CD with GitHub Actions (tests + lint)
- Dependabot for dependency updates
- SECURITY.md, CONTRIBUTING.md, CHANGELOG.md
- Sample report (Flask) in README

### Changed
- Default model switched from Claude Sonnet to Gemini 2.5 Flash (free)
- File tree truncated to 500 files for large repos
- Retry on rate limit (60s backoff)

## [0.1.0] - 2026-03-29

### Added
- ReAct agent loop (from scratch, no LangChain)
- 6 tools: get_repo_info, get_file_tree, get_file_content, search_code, analyze_dependencies, check_security
- Pydantic report schema (8 dimensions, 1-10 scoring)
- Markdown report renderer
- CLI with Typer (analyze + eval commands)
- Eval framework with fixtures
