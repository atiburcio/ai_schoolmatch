from typing import Callable

from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_app.nodes.final_rec.prompt import HUMAN_MESSAGE, SYSTEM_MESSAGE
from langchain_app.utils.human_feedback import extract_feedback_history

from models.state import State


def create_final_recommender(llm: ChatOpenAI) -> Callable[[State], State]:
    """Creates a node that makes the final recommendation.
    
    Args:
        llm: Language model for final recommendation
        
    Returns:
        Callable that takes a State and returns updated state with final recommendation
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    
    chain = prompt | llm
    
    def final_recommender(state: State) -> State:
        """Generate final recommendation based on all analyses and feedback history."""
        try:
            response: AIMessage = chain.invoke({
                "ipeds_semantic_search": state.ipeds_semantic_search,
                "human_feedback": extract_feedback_history(state.messages),
                "run_name": "Final Recommendation"
            })
            return State(
                school=state.school,
                features=state.features,
                ipeds_semantic_search=state.ipeds_semantic_search,
                # recommendations=state.recommendations,
                final_recommendation=response.content,
                messages=state.messages + [response]
            )
        except Exception as e:
            print(f"Error in final recommender: {str(e)}")
            return State(
                school=state.school,
                features=state.features,
                ipeds_semantic_search=state.ipeds_semantic_search,
                # recommendations=state.recommendations,
                final_recommendation=""
            )
    
    return final_recommender
