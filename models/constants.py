"""Constants for the college models and analysis."""

from enum import Enum
from typing import Dict


class SectorType(str, Enum):
    """Enum for institution sector types."""
    PUBLIC_4YEAR = "Public, 4-year or above"
    PRIVATE_NONPROFIT_4YEAR = "Private nonprofit, 4-year or above"
    PRIVATE_FORPROFIT_4YEAR = "Private for-profit, 4-year or above"
    PUBLIC_2YEAR = "Public, 2-year"
    PRIVATE_NONPROFIT_2YEAR = "Private nonprofit, 2-year"
    PRIVATE_FORPROFIT_2YEAR = "Private for-profit, 2-year"
    PUBLIC_LESS_2YEAR = "Public, less than 2-year"
    PRIVATE_NONPROFIT_LESS_2YEAR = "Private nonprofit, less than 2-year"
    PRIVATE_FORPROFIT_LESS_2YEAR = "Private for-profit, less than 2-year"


class ProgramLevel(str, Enum):
    """Enum for program levels offered by institutions."""
    LESS_THAN_ONE_YEAR = "Less than one year certificate"
    ONE_TO_TWO_YEARS = "One but less than two years certificate"
    ASSOCIATES = "Associate's degree"
    TWO_TO_FOUR_YEARS = "Two but less than 4 years certificate"
    BACHELORS = "Bachelor's degree"
    POST_BACHELORS = "Postbaccalaureate certificate"
    MASTERS = "Master's degree"
    POST_MASTERS = "Post-master's certificate"
    RESEARCH_DOCTORATE = "Doctor's degree - research/scholarship"
    PROFESSIONAL_DOCTORATE = "Doctor's degree - professional practice"
    OTHER_DOCTORATE = "Doctor's degree - other"


SECTOR_MAP: Dict[int, str] = {
    1: SectorType.PUBLIC_4YEAR,
    2: SectorType.PRIVATE_NONPROFIT_4YEAR,
    3: SectorType.PRIVATE_FORPROFIT_4YEAR,
    4: SectorType.PUBLIC_2YEAR,
    5: SectorType.PRIVATE_NONPROFIT_2YEAR,
    6: SectorType.PRIVATE_FORPROFIT_2YEAR,
    7: SectorType.PUBLIC_LESS_2YEAR,
    8: SectorType.PRIVATE_NONPROFIT_LESS_2YEAR,
    9: SectorType.PRIVATE_FORPROFIT_LESS_2YEAR
}

PROGRAM_LEVELS: Dict[str, str] = {
    'LEVEL1': ProgramLevel.LESS_THAN_ONE_YEAR,
    'LEVEL2': ProgramLevel.ONE_TO_TWO_YEARS,
    'LEVEL3': ProgramLevel.ASSOCIATES,
    'LEVEL4': ProgramLevel.TWO_TO_FOUR_YEARS,
    'LEVEL5': ProgramLevel.BACHELORS,
    'LEVEL6': ProgramLevel.POST_BACHELORS,
    'LEVEL7': ProgramLevel.MASTERS,
    'LEVEL8': ProgramLevel.POST_MASTERS,
    'LEVEL17': ProgramLevel.RESEARCH_DOCTORATE,
    'LEVEL18': ProgramLevel.PROFESSIONAL_DOCTORATE,
    'LEVEL19': ProgramLevel.OTHER_DOCTORATE
}
