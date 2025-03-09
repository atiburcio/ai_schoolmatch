from typing import Annotated, Optional
from enum import Enum

from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langgraph.graph import START, END
from models import VectorDataBaseResults


class NodeName(str, Enum):
    FINAL_RECOMMENDER = "final_recommender"
    FEATURE_EXTRACTOR = "feature_extractor"
    WEB_SEARCH_TOOL = "web_search_tool"
    WIKIPEDIA_SEARCH = "wikipedia_search"
    IPEDS_SEARCH = "ipeds_search"
    RECOMMENDATION_FORMATTER = "recommendation_formatter"
    HUMAN_FEEDBACK = "human_feedback"
    START = START
    END = END


class State(BaseModel):
    """State definition for the school matcher graph"""
    messages: Annotated[list, add_messages] = []
    school: str
    features: str = ""
    ipeds_semantic_search: list[VectorDataBaseResults] = []
    recommendations: str = ""
    final_recommendation: str = ""


class HumanFeedbackSeparation(BaseModel):
    """Contains the human feedback for one task.
    
    Set feedback to None if no feedback was provided.
    """
    feedback: Optional[str] = Field(..., description="Human feedback for one task")

    @property
    def has_feedback(self):
        return any([self.feedback])