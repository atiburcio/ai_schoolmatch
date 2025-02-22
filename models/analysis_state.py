"""
Analysis State Models

This module contains Pydantic models for managing the state of merger analysis pipelines.
"""

from pydantic import BaseModel, Field


class VectorDataBaseResults(BaseModel):
    """Model for storing IPEDS semantic search analysis results for a potential partner institution."""
    school: str = Field(description="Name of the potential partner institution")
    location: str = Field(description="City and state of the institution")
    analysis: str = Field(description="Detailed compatibility analysis")
    similarity_score: float = Field(description="Vector similarity score (0-1)")


class AnalysisState(BaseModel):
    """Model for managing the state of the merger analysis pipeline."""
    school: str = Field(description="Name of the target institution")
    features: str = Field(default="", description="Extracted M&A-relevant features")
    ipeds_semantic_search: list[VectorDataBaseResults] = Field(
        default_factory=list,
        description="List of compatibility analyses with potential partners"
    )
    # recommendations: str = Field(default="", description="Formatted merger recommendations")
    final_recommendation: str = Field(default="", description="Final merger recommendation")
