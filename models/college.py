from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class College(BaseModel):
    id: str
    name: str
    location: str
    state: str
    type: str  # Public, Private, Community College
    total_enrollment: int
    acceptance_rate: float  # Percentage
    tuition_in_state: int  # Annual tuition in USD
    tuition_out_state: int  # Annual tuition in USD
    programs: List[str]  # Major programs offered
    student_faculty_ratio: float
    graduation_rate: float  # Percentage
    campus_setting: str  # Urban, Suburban, Rural
    athletics_division: str  # NCAA Division I, II, III, NAIA, etc.
    housing_available: bool
    description: str  # Detailed description of the college
    notable_features: List[str]  # Special programs, research opportunities, etc.
    median_sat_score: Optional[int]
    median_act_score: Optional[int]
    ranking_national: Optional[int]  # National ranking if available
    vector_embedding: Optional[List[float]] = None

    class Config:
        from_attributes = True
