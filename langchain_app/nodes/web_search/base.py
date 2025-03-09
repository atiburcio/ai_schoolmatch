from typing import Callable
import os

from langchain_core.messages import AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from models.state import State


@tool
def web_search(query: str) -> str:
    """Search the web for information about a query using Tavily."""
    tavily_search = TavilySearchResults(max_results=10)
    results = tavily_search.invoke(query)
    
    # Format the results
    formatted_results = "\n\n".join(
        [
            f'Source: {doc["url"]}\n{doc["content"]}'
            for doc in results
        ]
    )
    
    return formatted_results


def create_web_search_tool_node() -> Callable[[State], State]:
    """Creates a node that performs web searches to enhance feature information."""
    tools = [web_search]
    tool_node = ToolNode(tools)
    
    def web_search_with_state_update(state: State) -> State:
        """Execute web search and update state with results"""
        # Check if there's a message with tool calls
        tool_calls = None
        query = "general information about the school"
        
        # Extract query from tool calls if available
        for message in reversed(state.messages):
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = message.tool_calls
                # Extract the first tool call with name web_search
                for tool_call in tool_calls:
                    if tool_call.get('name') == 'web_search':
                        query = tool_call.get('args', {}).get('query', query)
                        break
                break
        
        # Execute the tool node with the query
        try:
            # Directly call the web search tool
            search_result = web_search(query)
            
            # Create a message with the results
            result_message = AIMessage(content=f"Web Search Results:\n\n{search_result}")
            
            # Return updated state
            return State(
                school=state.school,
                features=state.features,
                ipeds_semantic_search=state.ipeds_semantic_search,
                recommendations=state.recommendations,
                final_recommendation=state.final_recommendation,
                messages=state.messages + [result_message]
            )
        except Exception as e:
            print(f"Error executing web search: {str(e)}")
            error_message = AIMessage(content=f"Error performing web search: {str(e)}")
            return State(
                school=state.school,
                features=state.features,
                ipeds_semantic_search=state.ipeds_semantic_search,
                recommendations=state.recommendations,
                final_recommendation=state.final_recommendation,
                messages=state.messages + [error_message]
            )
    
    return web_search_with_state_update
