from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, List
from langchain_app.merger_analyzer import (
    create_merger_feature_extractor,
    create_compatibility_analyzer,
    create_merger_recommendation_formatter,
    create_final_recommender
)
from db.college_vector_store import CollegeVectorStore
import os
from dotenv import load_dotenv

class State(TypedDict):
    """State definition for the school matcher graph"""
    messages: Annotated[List, add_messages]
    school: str
    features: str
    compatibility_analyses: List[dict]
    recommendations: str
    final_recommendation: str

def create_school_matcher_graph(vector_store: CollegeVectorStore):
    """Creates the school matcher graph with all necessary nodes"""
    # Load environment variables
    load_dotenv()
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create the graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("merger_feature_extractor", create_merger_feature_extractor(llm))
    workflow.add_node("compatibility_analyzer", create_compatibility_analyzer(vector_store, llm))
    workflow.add_node("merger_recommendation_formatter", create_merger_recommendation_formatter(llm))
    workflow.add_node("final_recommender", create_final_recommender(llm))
    
    # Add edges
    workflow.add_edge("merger_feature_extractor", "compatibility_analyzer")
    workflow.add_edge("compatibility_analyzer", "merger_recommendation_formatter")
    workflow.add_edge("merger_recommendation_formatter", "final_recommender")
    workflow.add_edge("final_recommender", END)
    
    # Set the entry point
    workflow.set_entry_point("merger_feature_extractor")
    
    # Compile the graph
    return workflow.compile()

def run_school_matcher(graph, school_description: str):
    """Runs the school matcher graph with a given school description"""
    # Initialize the state with the school description and empty messages list
    state = {
        "messages": [],
        "school": school_description,
        "features": "",
        "compatibility_analyses": [],
        "recommendations": "",
        "final_recommendation": ""
    }
    
    # Run the graph
    final_state = graph.invoke(state)
    
    return final_state
