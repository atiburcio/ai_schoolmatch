import os
from typing import Annotated, TypedDict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_app.nodes.extract_target_features.base import create_feature_extractor
from langchain_app.nodes.compatibility_analyzer.base import create_compatibility_analyzer
from langchain_app.nodes.rec_formatter.base import create_recommendation_formatter
from langchain_app.nodes.final_rec.base import create_final_recommender
from langchain_app.nodes.human_feedback.base import create_human_feedback_node
from db.college_vector_store import CollegeVectorStore
from models.state import State



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
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("target_school_feature_extractor", create_feature_extractor(llm))
    graph_builder.add_node("compatibility_analyzer", create_compatibility_analyzer(vector_store, llm))
    graph_builder.add_node("merger_recommendation_formatter", create_recommendation_formatter(llm))
    graph_builder.add_node("final_recommender", create_final_recommender(llm))

    # Add nodes with edges
    graph_builder.add_node("human_feedback", create_human_feedback_node())
    
    # Add edges
    graph_builder.add_edge("target_school_feature_extractor", "compatibility_analyzer")
    graph_builder.add_edge("compatibility_analyzer", "merger_recommendation_formatter")
    graph_builder.add_edge("merger_recommendation_formatter", "final_recommender")
    graph_builder.add_edge("final_recommender", "human_feedback")
    graph_builder.add_edge("human_feedback", END)
    
    # Set the entry point
    graph_builder.set_entry_point("target_school_feature_extractor")

    # create graph config

    
    # Compile the graph
    return graph_builder.compile(checkpointer=MemorySaver())

def run_school_matcher(graph, school_description: str, config: dict):
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
    final_state = graph.invoke(state, config=config)
    
    return final_state

def create_graph_config() -> dict:
    return {
        "configurable": {"thread_id": "1"},
    }