"""Pydantic models for the due diligence report.

Defines the exact structure the agent must produce.
Pydantic validates the data AND generates a JSON Schema for the LLM API.
"""

from pydantic import BaseModel, Field


class Finding(BaseModel):
    """A concrete observation within a dimension."""

    detail: str = Field(description="Description of the observation")
    positive: bool = Field(description="True = strength, False = weakness")


class Dimension(BaseModel):
    """One of the 8 evaluation dimensions."""

    name: str = Field(description="Dimension name")
    score: int = Field(ge=1, le=10, description="Score from 1 (very bad) to 10 (excellent)")
    findings: list[Finding] = Field(description="Concrete observations")
    recommendation: str = Field(description="Actionable recommendation for this dimension")


class RepoInfo(BaseModel):
    """Basic metadata of the analyzed repo."""

    name: str
    owner: str
    description: str | None = None
    language: str | None = None
    stars: int
    forks: int
    created_at: str
    license: str | None = None


class DiligenceReport(BaseModel):
    """Complete technical due diligence report."""

    repo_info: RepoInfo = Field(description="Repository metadata")
    dimensions: list[Dimension] = Field(
        min_length=8,
        max_length=8,
        description="The 8 evaluation dimensions",
    )
    overall_score: float = Field(
        ge=1, le=10, description="Overall score (weighted average of dimensions)"
    )
    verdict: str = Field(
        description="Strong Invest | Invest with Caution | Pass | Needs More Investigation"
    )
    summary: str = Field(description="Overall summary in a few sentences")
