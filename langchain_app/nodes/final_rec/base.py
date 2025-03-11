from typing import Callable, Literal
import os

from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from langchain_app.nodes.final_rec.prompt import HUMAN_MESSAGE, SYSTEM_MESSAGE
from langchain_app.nodes.web_search.base import web_search
from langchain_app.utils.human_feedback import extract_feedback_history

from models.state import State, NodeName


def create_final_recommender() -> Callable[
    [State], Command[Literal[NodeName.WEB_SEARCH_TOOL, NodeName.HUMAN_FEEDBACK]]
]:
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
    
    llm = ChatOpenAI(model="o3-mini", api_key=os.getenv("OPENAI_API_KEY"))
    llm_with_tools = llm.bind_tools([web_search])
    runnnable = prompt | llm_with_tools
    
    def final_recommender(state: State) -> Command[Literal[NodeName.WEB_SEARCH_TOOL, NodeName.HUMAN_FEEDBACK]]:
        """Generate final recommendation based on all analyses and feedback history."""
        # Extract any web search results from previous messages
        web_search_results = []
        for msg in state.messages:
            if hasattr(msg, 'content') and isinstance(msg.content, str) and msg.content.startswith("Web Search Results:"):
                web_search_results.append(msg.content)
        
        web_search_info = "\n\n".join(web_search_results) if web_search_results else "No web search results available."
        
        # Invoke the chain with all available information
        response: AIMessage = runnnable.invoke({
            "ipeds_semantic_search": state.ipeds_semantic_search,
            "human_feedback": extract_feedback_history(state.messages),
            "web_search_results": web_search_info,
            "run_name": "Final Recommendation"
        })
        
        # Improved debugging
        print(f"\n\n=============== FINAL RECOMMENDER RESPONSE ===============")
        print(f"Response type: {type(response)}")
        print(f"Response attributes: {dir(response)}")
        print(f"Tool calls attribute exists: {hasattr(response, 'tool_calls')}")
        
        if hasattr(response, 'tool_calls'):
            print(f"Tool calls: {response.tool_calls}")
            if response.tool_calls:
                print(f"Found tool calls - directing to WEB_SEARCH node")
                # We found tool calls, go to web search
                updated_state = {"messages": state.messages + [response]}
                return Command(update=updated_state, goto=NodeName.WEB_SEARCH_TOOL)
        
        # No tool calls, proceed to human feedback
        print(f"No tool calls found - proceeding to HUMAN_FEEDBACK node")
        updated_state = {"messages": state.messages + [response], "final_recommendation": response.content}
        return Command(update=updated_state, goto=NodeName.HUMAN_FEEDBACK)
    
    return final_recommender
