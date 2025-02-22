from typing import Callable

from langchain.prompts.chat import (
    ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from db.college_vector_store import CollegeVectorStore
from langchain_app.nodes.extract_target_features.prompt import HUMAN_MESSAGE, SYSTEM_MESSAGE

from models.state import State
 
def create_feature_extractor(llm: ChatOpenAI, vector_store: CollegeVectorStore) -> Callable[[State], State]:
    """Creates a node that extracts M&A-relevant features from the target institution.
    
    Args:
        llm: Language model for feature extraction
        vector_store: Vector store containing IPEDS data
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with extracted features
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    
    chain = prompt | llm
    
    def feature_extractor(state: State) -> State:
        """Extract features from the school description and IPEDS data."""
        try:
            # Query vector store for target school data
            results = vector_store.find_similar_colleges(state.school, n_results=1)
            ipeds_data = results[0]["document"] if results else "No IPEDS data found"

            response: AIMessage = chain.invoke({
                "school": state.school,
                "description": state.school,  # Using the original description
                "ipeds_data": ipeds_data,
                "run_name": "Feature Extraction"
            })
            return State(
                school=state.school,
                features=response.content,
                ipeds_semantic_search=[],
                recommendations="",
                final_recommendation="",
                messages=state.messages + [response]  # Preserve existing messages and add new one
            )
        except Exception as e:
            print(f"Error in feature extraction: {str(e)}")
            return State(
                school=state.school,
                features="",
                ipeds_semantic_search=[],
                recommendations="",
                final_recommendation=""
            )
    
    return feature_extractor
