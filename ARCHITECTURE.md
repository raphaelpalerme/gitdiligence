# GitDiligence — Agent de Due Diligence Technique

## Contexte
Un agent IA autonome qui analyse des repos GitHub et produit un rapport de due diligence technique structuré. Projet portfolio pour démontrer la maîtrise de l'orchestration LLM, du pattern ReAct, et du prompt engineering — construit from scratch, sans LangChain.

---

## Input / Output

- **Input** : URL GitHub ou `owner/repo`
- **Output** : Rapport structuré (Markdown + JSON) avec scores 1-10 par dimension

---

## Architecture

```
src/gitdiligence/
├── __init__.py
├── __main__.py              # python -m gitdiligence
├── cli.py                   # CLI (typer)
├── agent/
│   ├── react.py             # Boucle ReAct (coeur du projet)
│   ├── state.py             # AgentState + Step dataclasses
│   └── prompts.py           # System prompt
├── llm/
│   └── client.py            # Wrapper Claude API (messages + tool_use)
├── tools/
│   ├── base.py              # Classe abstraite Tool
│   ├── registry.py          # ToolRegistry (collecte + dispatch)
│   ├── github_api.py        # get_repo_info, get_contributors, get_commit_activity, get_languages
│   ├── github_contents.py   # get_file_tree, get_file_content
│   ├── dependency.py        # parse_dependencies
│   ├── security.py          # check_security_signals
│   └── search.py            # search_code (GitHub code search)
├── report/
│   ├── schema.py            # Modèles Pydantic (DueDiligenceReport)
│   └── renderer.py          # Markdown renderer
└── eval/
    ├── runner.py             # Exécute l'agent sur des repos connus
    ├── criteria.py           # Scoring (completeness, accuracy, cost)
    └── fixtures/
        └── known_repos.json  # Ground truth pour l'éval
```

---

## Boucle ReAct

```
1. Message initial : system prompt + "Analyse le repo X"
2. BOUCLE (max 25 itérations) :
   a. Appel Claude avec messages + tools
   b. Parse response.content :
      - TextBlock → thought (raisonnement)
      - ToolUseBlock → tool_name + tool_input
   c. Si tool == "generate_report" → valide le rapport, FIN
   d. Sinon → exécute l'outil, enregistre le Step, append aux messages
3. Si max atteint → force generate_report
4. Retourne AgentState (steps, rapport, tokens)
```

**Terminaison** : l'agent appelle `generate_report` (un outil spécial) qui valide le rapport via Pydantic et termine la boucle.

---

## 10 Outils de l'agent

| # | Outil | Description |
|---|-------|-------------|
| 1 | `get_repo_info` | Métadonnées (stars, forks, license, dates, topics) |
| 2 | `get_contributors` | Liste contributeurs + nombre de commits |
| 3 | `get_commit_activity` | Activité hebdo sur 1 an |
| 4 | `get_languages` | Répartition des langages |
| 5 | `get_file_tree` | Arborescence du repo (profondeur configurable) |
| 6 | `get_file_content` | Contenu d'un fichier spécifique |
| 7 | `search_code` | Recherche de patterns dans le code (GitHub search) |
| 8 | `parse_dependencies` | Analyse des manifests (requirements.txt, package.json...) |
| 9 | `check_security_signals` | .env commités, SECURITY.md, dependabot, patterns suspects |
| 10 | `generate_report` | Produit le rapport final (schema Pydantic = input_schema) |

---

## Rapport — 8 dimensions avec score 1-10

1. **Repo Health** : stars, forks, activité, license, bus factor
2. **Code Quality** : langages, structure, tests, linter
3. **Dependencies** : nombre, manifests, dépendances notables
4. **Contributors** : distribution, commits récents, bus factor
5. **Documentation** : README, docs/, CONTRIBUTING, CHANGELOG
6. **CI/CD & DevOps** : CI provider, Docker, IaC
7. **Security** : policy, dependabot, secrets, .env
8. **Overall Assessment** : score global, forces, risques, recommandation

Recommandation finale : `Strong Invest` / `Invest with Caution` / `Pass` / `Needs More Investigation`

---

## Stack technique

```toml
dependencies = [
    "anthropic>=0.86",      # Claude API avec tool_use natif
    "httpx>=0.28",          # HTTP client pour GitHub API
    "pydantic>=2.12",       # Validation rapport + génération JSON Schema
    "typer>=0.24",          # CLI (type hints, cohérent avec Pydantic)
    "rich>=14.0",           # Output terminal (progress, markdown)
]
```

Modèle par défaut : `claude-sonnet-4-6` (configurable via `--model`)

---

## CLI

```bash
gitdiligence analyze <owner/repo>       # Analyse un repo
    --model TEXT                      # Modèle LLM [claude-sonnet-4-6]
    --max-steps INT                   # Max itérations ReAct [25]
    --output-dir PATH                 # Dossier output [./reports]
    --format [md|json|both]           # Format [both]
    --verbose                         # Affiche le raisonnement en temps réel

gitdiligence eval                       # Évaluation sur repos connus
```

---

## Scope V1 (maintenant)

- Squelette projet complet
- 10 outils fonctionnels
- Boucle ReAct avec state management
- Rapport Pydantic + rendu Markdown
- CLI `analyze`
- Éval basique (3-5 repos fixtures)

## V2 (plus tard)

- Streaming output temps réel
- Exécution parallèle d'outils
- Lookup vulnérabilités (OSV.dev API)
- Web UI (Streamlit)
- Mode comparaison (2 repos côte à côte)

---

## Ordre d'implémentation

1. Squelette projet (pyproject.toml, .gitignore, .env.example)
2. `tools/base.py` + `tools/registry.py`
3. Outils GitHub (`github_api.py`, `github_contents.py`, `search.py`)
4. Outils restants (`dependency.py`, `security.py`)
5. `report/schema.py` (modèles Pydantic)
6. `llm/client.py`
7. `agent/prompts.py`
8. `agent/state.py`
9. `agent/react.py` (coeur du projet)
10. `report/renderer.py`
11. Outil `generate_report` (branche la schema Pydantic)
12. `cli.py` + `__main__.py`
13. Framework d'éval
14. CLAUDE.md + README

## Vérification

```bash
# Installer le projet
pip install -e ".[dev]"

# Lancer une analyse
export ANTHROPIC_API_KEY=sk-...
export GITHUB_TOKEN=ghp_...
gitdiligence analyze anthropics/anthropic-sdk-python --verbose

# Lancer les tests
pytest tests/

# Lancer l'éval
gitdiligence eval
```
