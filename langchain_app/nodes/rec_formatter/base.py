from typing import Callable

from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_app.nodes.extract_target_features.prompt import HUMAN_TEMPLATE, SYSTEM_TEMPLATE

from models import AnalysisState


def create_recommendation_formatter(llm: ChatOpenAI) -> Callable[[AnalysisState], AnalysisState]:
    """Creates a node that formats merger recommendations.
    
    Args:
        llm: Language model for formatting recommendations
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with formatted recommendations
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE),
        HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE),
    ])
    
    chain = prompt | llm
    
    def recommendation_formatter(state: AnalysisState) -> AnalysisState:
        """Format recommendations based on compatibility analyses."""
        try:
            response: AIMessage = chain.invoke({
                "compatibility_analyses": str([analysis.model_dump() for analysis in state.compatibility_analyses]),
                "run_name": "Recommendation Formatting"
            })
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations=response.content,
                final_recommendation=state.final_recommendation
            )
        except Exception as e:
            print(f"Error in recommendation formatter: {str(e)}")
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations="",
                final_recommendation=state.final_recommendation
            )
    
    return recommendation_formatter