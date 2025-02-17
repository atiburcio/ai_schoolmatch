import os
from copy import deepcopy
from typing import Annotated, TypedDict, List
from time import sleep

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langchain_core.messages import BaseMessage

from langchain_app.nodes.extract_target_features.base import create_feature_extractor
from langchain_app.nodes.compatibility_analyzer.base import create_compatibility_analyzer
from langchain_app.nodes.rec_formatter.base import create_recommendation_formatter
from langchain_app.nodes.final_rec.base import create_final_recommender
from langchain_app.nodes.human_feedback.base import create_human_feedback_node, EMPTY_INPUT_MSG
from db.college_vector_store import CollegeVectorStore
from models.state import State, NodeName


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
    graph_builder.add_node(NodeName.FEATURE_EXTRACTOR, create_feature_extractor(llm))
    graph_builder.add_node(NodeName.COMPATIBILITY_ANALYZER, create_compatibility_analyzer(vector_store, llm))
    graph_builder.add_node(NodeName.RECOMMENDATION_FORMATTER, create_recommendation_formatter(llm))
    graph_builder.add_node(NodeName.FINAL_RECOMMENDER, create_final_recommender(llm))

    # Add nodes with edges
    graph_builder.add_node(NodeName.HUMAN_FEEDBACK, create_human_feedback_node())
    
    # Add edges
    graph_builder.add_edge(NodeName.FEATURE_EXTRACTOR, NodeName.COMPATIBILITY_ANALYZER)
    graph_builder.add_edge(NodeName.COMPATIBILITY_ANALYZER, NodeName.RECOMMENDATION_FORMATTER)
    graph_builder.add_edge(NodeName.RECOMMENDATION_FORMATTER, NodeName.FINAL_RECOMMENDER)
    graph_builder.add_edge(NodeName.FINAL_RECOMMENDER, NodeName.HUMAN_FEEDBACK)
    
    # Set the entry point
    graph_builder.set_entry_point(NodeName.FEATURE_EXTRACTOR)

    # create graph config

    
    # Compile the graph
    return graph_builder.compile(checkpointer=MemorySaver())


def run_school_matcher(graph: CompiledStateGraph, school_description: str, config: dict) -> None:
    """Runs the school matcher graph with a given school description"""
    config = deepcopy(config)
    config["run_name"] = "School Matcher"

    #TODO: add callbacks here to handle langsmith tracing here rather in the notebook
    graph.invoke({"messages": [], "school": school_description}, config=config)


    while graph.get_state(config).next:

        current_state = graph.get_state(config).values
        messages: list[BaseMessage] = current_state["messages"]
        
        print(messages[-1].content)

        sleep(0.5)

        #get human feedback
        human_feedback_text = input("Feedback: ")
        human_feedback_text = human_feedback_text or EMPTY_INPUT_MSG
        if human_feedback_text != EMPTY_INPUT_MSG:
            print(f"\nFeedback: {human_feedback_text}\n\n")
        else:
            print("\nNo feedback provided\n")

        config["run_name"] = "Human Feedback"

        #invoke with human feedback
        graph.invoke(Command(resume=human_feedback_text), config=config)
    
    last_message: BaseMessage = graph.get_state(config).values["messages"][-1]
    print(f"\n*** Final Recommendation ***\n{last_message.content}")


def create_graph_config() -> dict:
    return {
        "configurable": {"thread_id": "1"},
    }
