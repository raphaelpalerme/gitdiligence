# Contributing to GitDiligence

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/raphaelpalerme/gitdiligence.git
cd gitdiligence
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development Workflow

1. Create a branch from `develop`
2. Make your changes
3. Run tests: `pytest -v`
4. Run linter: `ruff check .`
5. Open a PR against `develop`

## Adding a New Tool

1. Create a class extending `Tool` in `src/gitdiligence/tools/`
2. Implement `name`, `description`, `parameters`, and `execute()`
3. Register it in `src/gitdiligence/tools/__init__.py`
4. Add tests in `tests/`

## Code Style

- Python 3.11+
- Ruff for linting (config in `pyproject.toml`)
- Keep it simple — no clever abstractions

## Reporting Issues

Open an issue on GitHub with:
- What you expected
- What happened
- Steps to reproduce
