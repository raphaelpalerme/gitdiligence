# Roadmap GitDiligence

## V1 — Terminée

- [x] Squelette projet
- [x] Tool + Registry
- [x] Outils GitHub (repo info, file tree, file content, search code)
- [x] Outils d'analyse (dépendances, sécurité)
- [x] Schema Pydantic (8 dimensions)
- [x] Client LLM (Claude tool_use)
- [x] System prompt
- [x] State management
- [x] Boucle ReAct
- [x] Renderer Markdown
- [x] CLI (analyze + eval)
- [x] Framework d'eval
- [x] README

---

## V1.1 — Outils manquants + quick wins

Outils prévus dans l'architecture mais pas encore implémentés, et retours de l'auto-analyse (score 5/10).

### Outils
- [ ] `get_contributors` — liste des contributeurs + nombre de commits
- [ ] `get_commit_activity` — activité hebdomadaire sur 1 an
- [ ] `get_languages` — répartition des langages (% par langage)

### Projet
- [ ] Licence (MIT ou Apache-2.0)
- [ ] CI/CD — GitHub Actions (tests + ruff lint)
- [ ] Dependabot (.github/dependabot.yml)
- [ ] SECURITY.md
- [ ] CONTRIBUTING.md
- [ ] CHANGELOG.md

---

## V1.2 — Robustesse

- [ ] Streaming output — afficher le raisonnement en temps réel au lieu d'attendre
- [ ] Caching des appels GitHub — éviter de relire les mêmes fichiers
- [ ] Support Go (go.mod), Rust (Cargo.toml), Ruby (Gemfile) dans `dependency.py`
- [ ] Gestion des gros fichiers (tronquer le contenu si > 100KB)

---

## V2 — Fonctionnalités

- [ ] Web UI (Streamlit ou FastAPI)
- [ ] Mode comparaison (2 repos côte à côte)
- [ ] Lookup vulnérabilités (OSV.dev API)
- [ ] Export PDF du rapport
- [ ] Historique des analyses (SQLite)

---

## Visibilité

- [x] Push sur GitHub
- [x] Support Gemini gratuit (PR #1)
- [ ] Screenshot/gif du output dans le README
- [ ] Post sur LinkedIn/Twitter avec un exemple d'analyse
