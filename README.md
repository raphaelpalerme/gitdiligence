# GitDiligence

Agent IA de due diligence technique pour repos GitHub. Analyse un repo et produit un rapport structuré avec un score sur 8 dimensions.

## Comment ça marche

GitDiligence utilise un agent ReAct (Reasoning + Acting) qui :

1. Explore un repo GitHub via l'API (métadonnées, arborescence, fichiers clés)
2. Analyse les dépendances, la CI/CD, la sécurité, la documentation
3. Produit un rapport avec 8 dimensions notées de 1 à 10 et un verdict final

L'agent est implémenté from scratch (pas de LangChain), avec support multi-provider : **Gemini** (gratuit) et **Claude** (payant, meilleure qualité).

## Les 8 dimensions

| Dimension | Ce qui est évalué |
|-----------|-------------------|
| Repo Health | Stars, forks, activité, licence, bus factor |
| Code Quality | Structure, tests, linter, typage |
| Dependencies | Nombre, manifests, dépendances à risque |
| Contributors | Distribution, commits récents |
| Documentation | README, docs/, CONTRIBUTING, CHANGELOG |
| CI/CD & DevOps | CI, Docker, IaC |
| Security | SECURITY.md, dependabot, secrets exposés |
| Overall Assessment | Score global, forces, risques |

Verdicts possibles : `Strong Invest` · `Invest with Caution` · `Pass` · `Needs More Investigation`

## Installation

```bash
git clone https://github.com/raphaelpalerme/gitdiligence.git
cd gitdiligence
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Crée un fichier `.env` à la racine :

```
GOOGLE_API_KEY=AIza...    # Gratuit — https://aistudio.google.com
GITHUB_TOKEN=ghp_...

# Optionnel — seulement pour --model claude-sonnet-4-6
ANTHROPIC_API_KEY=sk-ant-...
```

## Utilisation

```bash
# Analyser un repo (Gemini, gratuit)
gitdiligence analyze pallets/flask

# Avec le raisonnement en temps réel
gitdiligence analyze pallets/flask --verbose

# Utiliser Claude (payant, meilleure qualité)
gitdiligence analyze pallets/flask --model claude-sonnet-4-6

# Lancer l'évaluation
gitdiligence eval
```

Les rapports sont sauvegardés dans `./reports/` (Markdown + JSON).

## Stack

- **Agent** : boucle ReAct from scratch (pas de LangChain)
- **LLM** : Gemini (gratuit) ou Claude (payant), multi-provider avec abstraction normalisée
- **GitHub** : httpx + GitHub REST API v3
- **Validation** : Pydantic (rapport + JSON Schema pour les outils)
- **CLI** : Typer + Rich

## Structure

```
src/gitdiligence/
├── agent/
│   ├── prompts.py      # System prompt
│   ├── state.py        # State management (steps, tokens)
│   └── react.py        # Boucle ReAct
├── llm/
│   ├── client.py       # Dispatcher multi-provider (Claude + Gemini)
│   └── models.py       # Types normalisés (LLMResponse, ToolCall)
├── tools/
│   ├── base.py         # Classe abstraite Tool
│   ├── registry.py     # Registre d'outils
│   ├── github_api.py   # Client HTTP GitHub
│   ├── github_contents.py  # get_repo_info, get_file_tree, get_file_content
│   ├── search.py       # search_code
│   ├── dependency.py   # analyze_dependencies
│   └── security.py     # check_security
├── report/
│   ├── schema.py       # Modèles Pydantic du rapport
│   └── renderer.py     # Rendu Markdown
├── eval/
│   ├── fixtures.py     # Repos de référence
│   └── runner.py       # Runner d'évaluation
├── cli.py              # CLI (Typer)
└── __main__.py         # python -m gitdiligence
```

## Tests

```bash
pytest -v
```
