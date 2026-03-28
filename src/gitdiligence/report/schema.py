"""Modèles Pydantic du rapport de due diligence.

Définit la structure exacte du rapport que l'agent doit produire.
Pydantic valide les données ET génère un JSON Schema pour l'API Claude.
"""

from pydantic import BaseModel, Field


class Finding(BaseModel):
    """Une observation concrète dans une dimension."""

    detail: str = Field(description="Description de l'observation")
    positive: bool = Field(description="True = point fort, False = point faible")


class Dimension(BaseModel):
    """Une des 8 dimensions d'évaluation."""

    name: str = Field(description="Nom de la dimension")
    score: int = Field(ge=1, le=10, description="Score de 1 (très mauvais) à 10 (excellent)")
    findings: list[Finding] = Field(description="Observations concrètes")
    recommendation: str = Field(description="Conseil actionnable pour cette dimension")


class RepoInfo(BaseModel):
    """Métadonnées basiques du repo analysé."""

    name: str
    owner: str
    description: str | None = None
    language: str | None = None
    stars: int
    forks: int
    created_at: str
    license: str | None = None


class DiligenceReport(BaseModel):
    """Rapport complet de due diligence technique."""

    repo_info: RepoInfo = Field(description="Métadonnées du repo")
    dimensions: list[Dimension] = Field(
        min_length=8,
        max_length=8,
        description="Les 8 dimensions d'évaluation",
    )
    overall_score: float = Field(
        ge=1, le=10, description="Score global (moyenne pondérée des dimensions)"
    )
    verdict: str = Field(
        description="Strong Invest | Invest with Caution | Pass | Needs More Investigation"
    )
    summary: str = Field(description="Synthèse globale en quelques phrases")
