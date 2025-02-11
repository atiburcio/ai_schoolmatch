"""Models package for core domain entities."""

from .college import College
from .analysis_state import AnalysisState, CompatibilityAnalysis

__all__ = ['College', 'AnalysisState', 'CompatibilityAnalysis']
