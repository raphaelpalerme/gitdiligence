# Due Diligence: pallets/flask

## Repo
- **Description**: The Python micro framework for building web applications.
- **Language**: Python
- **Stars**: 71,354
- **Forks**: 16,757
- **License**: BSD-3-Clause
- **Created**: 2010-04-06T11:11:59Z

## Repo Health (10/10)

  + 71,354 stars and 16,757 forks — one of the most starred Python web frameworks on GitHub
  + Project has been continuously active since April 2010 — over 15 years of sustained maintenance
  + BSD-3-Clause license: permissive, business-friendly, and well-known
  + Only 3 open issues — extremely healthy issue hygiene
  + Current version is 3.2.0.dev (main) with 3.1.3 being the latest stable release (2026-02-18)
  + 61 commits over the last year across 24 active weeks — consistent cadence, not stagnant
  + Backed by the Pallets organization, a well-recognized open-source stewardship group

**Recommendation**: No concerns here. Flask's repo health is exemplary — high stars, long history, active maintainership, and a permissive license.

## Code Quality (9/10)

  + 99.9% Python codebase — extremely focused and purpose-built (sourced from get_languages)
  + Clean src-layout structure under src/flask/ with well-separated modules (app.py, blueprints.py, cli.py, ctx.py, sessions.py, etc.)
  + Dedicated sansio/ sub-package (sansio/app.py, sansio/blueprints.py, sansio/scaffold.py) demonstrates architectural maturity and testability
  + py.typed marker (src/flask/py.typed) confirms full PEP 561 typing support
  + Strict type checking via both mypy (strict mode) and pyright (basic mode), configured in pyproject.toml
  + Linting with Ruff (bugbear, pyflakes, pyupgrade, isort, pycodestyle) enforced through pre-commit hooks and CI
  + Comprehensive test suite: 20+ test files covering app context, async, blueprints, CLI, config, helpers, JSON, logging, sessions, signals, templating, views, and type checking
  + Tests run against minimum and development (git main) dependency versions via tox, in addition to stable versions
  + Coverage configured with branch coverage (pyproject.toml [tool.coverage])
  - No Dockerfile in the repo — not a weakness for a library, but worth noting

**Recommendation**: Code quality is excellent. The strict typing, multi-tool linting, and broad test coverage set a high bar. No significant improvements are needed.

## Dependencies (10/10)

  + Only 6 runtime dependencies: blinker, click, itsdangerous, jinja2, markupsafe, werkzeug — all from the Pallets ecosystem or trusted projects
  + All dependencies are Pallets-owned or well-established, minimizing supply chain risk
  + Minimum version pins are specific (e.g., werkzeug>=3.1.0) while allowing flexibility — no overly tight constraints
  + Optional extras clearly separated: 'async' (asgiref) and 'dotenv' (python-dotenv)
  + uv.lock file present — reproducible installs guaranteed
  - No dependabot.yml file found in .github/ — automated PR-based dependency update alerts are not configured
  + Dev dependencies use tox-uv, ruff, mypy, pyright, pytest — all modern and well-maintained tools

**Recommendation**: Dependency footprint is minimal and extremely clean. Consider adding a dependabot.yml or equivalent to automate dependency update PRs.

## Contributors (8/10)

  + Top contributor 'davidism' has 1,826 commits — the primary current maintainer of the Pallets projects
  + Founder 'mitsuhiko' (Armin Ronacher) contributed 1,189 commits — strong founding lineage
  + 20 unique contributors shown; broader community involvement evidenced by additional historical contributors
  + pre-commit-ci[bot] (39 commits) and dependabot[bot]/dependabot-preview[bot] (152 combined) show automated tooling contributing to maintenance
  - Significant bus factor risk: top 2 contributors (davidism + mitsuhiko) account for ~73% of all commits among the top 20
  - Active development work is largely concentrated on 'davidism' — single point of failure for the current maintenance cycle
  + 61 commits in the last year across 24 weeks shows consistent, if moderate, activity

**Recommendation**: While community size is healthy, the bus factor is a real concern with ~73% of top commits from two individuals. The project would benefit from cultivating additional core maintainers.

## Documentation (10/10)

  + Extensive docs/ directory covering: quickstart, tutorial, blueprints, CLI, configuration, deployment (9 server options), error handling, logging, signals, testing, async/await, and web-security
  + Full tutorial with step-by-step instructions and screenshots (docs/tutorial/) with corresponding example code in examples/tutorial/
  + Comprehensive deployment docs for Apache HTTPD, ASGI, eventlet, gevent, gunicorn, mod_wsgi, nginx, uWSGI, and Waitress
  + docs/patterns/ covers 20+ common use-case patterns including SQLAlchemy, Celery, file uploads, caching, stream, etc.
  + .readthedocs.yaml present — auto-builds docs on Read the Docs
  + CHANGES.rst contains a detailed, well-maintained changelog going back to version 0.1 (April 2010) with GitHub issue/PR references
  + Contributing docs reference the Pallets contributing guide at palletsprojects.com/contributing/
  + README is concise but functional — includes quick-start example and links to full documentation
  - No SECURITY.md in the repository itself — security policy is likely handled at the org level but not discoverable from the repo

**Recommendation**: Documentation is world-class and among the best in the Python ecosystem. Consider adding a SECURITY.md to the repository to make the vulnerability disclosure process immediately discoverable.

## CI/CD & DevOps (9/10)

  + GitHub Actions CI (tests.yaml) runs on 11 matrix configurations: Python 3.10–3.14, 3.14t (free-threaded), PyPy 3.11, Windows, macOS, minimum dependency versions, and development dependency versions
  + CI is triggered on PRs (excluding docs/README changes) and pushes to main/stable — smart path filtering reduces unnecessary runs
  + Dedicated typing job runs both mypy and pyright in CI (tests.yaml)
  + Automated publish pipeline (publish.yaml): builds on tag push, creates GitHub draft release, and publishes to PyPI using OIDC trusted publishing (no stored secrets)
  + All GitHub Actions pins use commit SHA hashes, not mutable version tags — supply chain attack hardening
  + zizmor.yaml: dedicated workflow running zizmor-action for GitHub Actions security analysis on every YAML change
  + pre-commit.yaml workflow for automated pre-commit checks (ruff, codespell, uv-lock, merge conflict detection, etc.)
  + lock.yaml workflow likely handles automatic stale issue/PR locking
  - No Docker/container CI artifacts — expected for a library but noted
  + concurrency groups with cancel-in-progress prevent redundant CI runs on fast-push scenarios

**Recommendation**: CI/CD setup is excellent and showcases modern best practices (SHA-pinned actions, OIDC publishing, matrix testing, security scanning). No critical gaps identified.

## Security (8/10)

  + All GitHub Actions steps use SHA-pinned action versions (e.g., actions/checkout@de0fac2e...) to prevent supply chain attacks
  + PyPI publishing uses OIDC trusted publishing (id-token: write) — no long-lived PyPI API tokens stored as secrets
  + zizmor security scanner for GitHub Actions workflows is run in CI on every YAML change
  + persist-credentials: false on all checkout actions minimizes token leakage risk
  + permissions: {} set at the top of every workflow — principle of least privilege enforced
  + itsdangerous is a core dependency — Flask sessions are cryptographically signed by design
  + CHANGES.rst references GitHub Security Advisories (ghsa:) for security fixes (e.g., 3.1.3 ghsa-68rp-wp8r-4726, 3.1.1 ghsa-4grg-w6v8-c28g)
  - No SECURITY.md file in the repository — vulnerability disclosure process is not immediately discoverable from the repo
  - No dependabot.yml — automated dependency vulnerability alerts via Dependabot PRs are not configured in-repo
  - tests/test_apps/.env file is committed to the repo — while this is a test fixture, .env files in repos can be a confusing signal and should be clearly scoped

**Recommendation**: Security posture is strong, particularly in CI/CD supply chain protection. Add a SECURITY.md to document the responsible disclosure process. Consider adding dependabot.yml for automated dependency vulnerability alerts.

## Overall Assessment (9/10)

  + Flask is one of the most widely-used Python web frameworks with 71k+ stars, 15+ years of active maintenance, and the backing of the Pallets organization
  + Minimal, well-designed dependency graph (6 runtime deps, all from trusted Pallets ecosystem)
  + World-class documentation with tutorials, patterns, and full deployment guides
  + Modern DevOps practices: SHA-pinned CI, OIDC publishing, zizmor security scanning, tox matrix testing across 11 environments
  + Strong typing with py.typed marker, mypy strict mode, and pyright in CI
  - Bus factor risk: current maintenance is highly concentrated on a single active maintainer (davidism)
  - No SECURITY.md file directly in the repository
  - No dependabot.yml for automated dependency update pull requests

**Recommendation**: Flask is a Strong Invest. It is a battle-tested, production-grade framework that is among the best-maintained Python libraries. The primary risks (bus factor, missing SECURITY.md) are minor and common in open-source projects of this type.

---
## Overall Score: 9.1/10
## Verdict: Strong Invest

Flask (pallets/flask) is a flagship Python micro web framework with 71,000+ stars, 15+ years of continuous development, and backing from the Pallets open-source organization. The codebase is clean, strictly typed, comprehensively tested across 11 CI matrix configurations, and ships with world-class documentation. Its dependency footprint is minimal (6 runtime dependencies, all trusted Pallets packages), its CI/CD pipeline employs modern supply-chain hardening (SHA-pinned actions, OIDC publishing, zizmor security scanning), and its changelog is meticulously maintained. The primary concerns are a moderately high bus factor (current maintenance concentrated around one key contributor), absence of a SECURITY.md policy file in the repo, and no dependabot.yml for automated dependency alerts — all minor for a project of this maturity. Flask is a strong choice for production use and represents very low adoption risk.