from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, List
from langchain_app.nodes.extract_target_features.base import create_feature_extractor
from langchain_app.nodes.compatibility_analyzer.base import create_compatibility_analyzer
from langchain_app.nodes.rec_formatter.base import create_recommendation_formatter
from langchain_app.nodes.final_rec.base import create_final_recommender
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
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create the graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("target_school_feature_extractor", create_feature_extractor(llm))
    workflow.add_node("compatibility_analyzer", create_compatibility_analyzer(vector_store, llm))
    workflow.add_node("merger_recommendation_formatter", create_recommendation_formatter(llm))
    workflow.add_node("final_recommender", create_final_recommender(llm))
    
    # Add edges
    workflow.add_edge("target_school_feature_extractor", "compatibility_analyzer")
    workflow.add_edge("compatibility_analyzer", "merger_recommendation_formatter")
    workflow.add_edge("merger_recommendation_formatter", "final_recommender")
    workflow.add_edge("final_recommender", END)
    
    # Set the entry point
    workflow.set_entry_point("target_school_feature_extractor")
    
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
