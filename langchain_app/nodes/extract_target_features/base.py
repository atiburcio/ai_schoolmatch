
from typing import Callable

from langchain.prompts.chat import (
    ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_app.nodes.extract_target_features.prompt import HUMAN_MESSAGE, SYSTEM_MESSAGE

from models import AnalysisState

def create_feature_extractor(llm: ChatOpenAI) -> Callable[[AnalysisState], AnalysisState]:
    """Creates a node that extracts M&A-relevant features from the target institution.
    
    Args:
        llm: Language model for feature extraction
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with extracted features
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    
    chain = prompt | llm
    
    def feature_extractor(state: AnalysisState) -> AnalysisState:
        """Extract features from the school description."""
        try:
            response: AIMessage = chain.invoke({
                "school": state.school,
                "run_name": "Feature Extraction"
            })
            return AnalysisState(
                school=state.school,
                features=response.content,
                compatibility_analyses=[],
                recommendations="",
                final_recommendation=""
            )
        except Exception as e:
            print(f"Error in feature extractor: {str(e)}")
            return AnalysisState(school=state.school)
    
    return feature_extractor
