from typing import Callable

from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_app.nodes.rec_formatter.prompt import HUMAN_MESSAGE, SYSTEM_MESSAGE

from models.state import State


def create_recommendation_formatter(llm: ChatOpenAI) -> Callable[[State], State]:
    """Creates a node that formats merger recommendations.
    
    Args:
        llm: Language model for formatting recommendations
        
    Returns:
        Callable that takes a State and returns updated state with formatted recommendations
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    
    chain = prompt | llm
    
    def recommendation_formatter(state: State) -> State:
        """Format recommendations based on compatibility analyses."""
        try:
            response: AIMessage = chain.invoke({
                "compatibility_analyses": str([analysis.model_dump() for analysis in state.compatibility_analyses]),
                "run_name": "Recommendation Formatting"
            })
            return State(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations=response.content,
                final_recommendation=state.final_recommendation
            )
        except Exception as e:
            print(f"Error in recommendation formatter: {str(e)}")
            return State(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations="",
                final_recommendation=state.final_recommendation
            )
    
    return recommendation_formatter