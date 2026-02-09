import os
from copy import deepcopy
from time import sleep

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langchain_core.messages import BaseMessage

from langchain_app.nodes.extract_target_features.base import create_feature_extractor
from langchain_app.nodes.ipeds_semantic_search.base import create_ipeds_semantic_search
from langchain_app.nodes.final_rec.base import create_final_recommender
from langchain_app.nodes.web_search.base import create_web_search_tool_node
from langchain_app.nodes.human_feedback.base import create_human_feedback_node, EMPTY_INPUT_MSG
from db.college_vector_store import CollegeVectorStore
from models.state import State, NodeName


def create_school_matcher_graph(vector_store: CollegeVectorStore):
    """Creates the school matcher graph."""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize the LLMs
    llm = ChatOpenAI(
        model="gpt-4.1-mini-2025-04-14",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create the graph
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node(NodeName.FEATURE_EXTRACTOR, create_feature_extractor(llm, vector_store))
    graph_builder.add_node(NodeName.IPEDS_SEARCH, create_ipeds_semantic_search(vector_store, llm))
    graph_builder.add_node(NodeName.WEB_SEARCH_TOOL, create_web_search_tool_node())
    
    # Add nodes with edges
    graph_builder.add_node(NodeName.FINAL_RECOMMENDER, create_final_recommender())
    graph_builder.add_node(NodeName.HUMAN_FEEDBACK, create_human_feedback_node())
    
    # Add edges
    graph_builder.add_edge(NodeName.FEATURE_EXTRACTOR, NodeName.IPEDS_SEARCH)
    graph_builder.add_edge(NodeName.IPEDS_SEARCH, NodeName.FINAL_RECOMMENDER)
    graph_builder.add_edge(NodeName.WEB_SEARCH_TOOL, NodeName.FINAL_RECOMMENDER)
    
    # Set the entry point
    graph_builder.set_entry_point(NodeName.FEATURE_EXTRACTOR)
    
    # Compile the graph
    return graph_builder.compile(checkpointer=MemorySaver())


def run_school_matcher(graph: CompiledStateGraph, school_description: str, config: dict) -> None:
    """Runs the school matcher graph with a given school description"""
    config = deepcopy(config)
    config["run_name"] = "School Matcher"

    #Initial invocation with school description
    graph.invoke({"messages": [], "school": school_description}, config=config)

    feedback_provided = False
    while graph.get_state(config).next:
        current_state = graph.get_state(config).values
        messages: list[BaseMessage] = current_state["messages"]
        
        if not messages:
            print("No messages in state, continuing...")
            continue
            
        # Print the last message content
        last_message = messages[-1]
        print(last_message.content)
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print("\nPerforming web search to gather more information...\n")
            # Just send an empty command to continue with the tool processing
            graph.invoke(Command(resume=""), config=config)
            continue

        sleep(0.5)

        #get human feedback
        human_feedback_text = input("Feedback (press Enter to continue without feedback): ")
        human_feedback_text = human_feedback_text or EMPTY_INPUT_MSG
        if human_feedback_text != EMPTY_INPUT_MSG:
            print(f"\nFeedback: {human_feedback_text}\n\n")
            feedback_provided = True
        else:
            print("\nNo feedback provided\n")
            feedback_provided = False

        config["run_name"] = "Human Feedback"

        #invoke with human feedback
        graph.invoke(Command(resume=human_feedback_text), config=config)
    
    if feedback_provided:
        last_message: BaseMessage = graph.get_state(config).values["messages"][-1]
        print(f"\n*** Final Recommendation ***\n{last_message.content}")


def create_graph_config() -> dict:
    return {
        "configurable": {"thread_id": "1"},
        "metadata": {"langsmith_project": "schoolmatch"},
        "callbacks": [],
    }
