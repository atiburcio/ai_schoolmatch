"""Models package for core domain entities."""

from .college import College
from .analysis_state import AnalysisState, CompatibilityAnalysis
from .constants import (
    SectorType,
    ProgramLevel,
    SECTOR_MAP,
    PROGRAM_LEVELS
)

__all__ = [
    'College',
    'AnalysisState',
    'CompatibilityAnalysis',
    'SectorType',
    'ProgramLevel',
    'SECTOR_MAP',
    'PROGRAM_LEVELS'
]
