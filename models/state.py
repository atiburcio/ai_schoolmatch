from typing import Annotated
from enum import Enum

from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langgraph.graph.node import START, END


class NodeName(str, Enum):
    FINAL_RECOMMENDER = "final_recommender"
    FEATURE_EXTRACTOR = "feature_extractor"
    COMPATIBILITY_ANALYZER = "compatibility_analyzer"
    RECOMMENDATION_FORMATTER = "recommendation_formatter"
    START = START
    END = END

class State(BaseModel):
    """State definition for the school matcher graph"""
    messages: Annotated[list, add_messages]
    school: str
    features: str
    compatibility_analyses: list[dict]
    recommendations: str
    final_recommendation: str