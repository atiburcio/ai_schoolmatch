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
    [State], Command[Literal[NodeName.WEB_SEARCH, NodeName.HUMAN_FEEDBACK]]
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
    
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
    llm_with_tools = llm.bind_tools([web_search])
    runnnable = prompt | llm_with_tools
    
    def final_recommender(state: State) -> Command[Literal[NodeName.WEB_SEARCH, NodeName.HUMAN_FEEDBACK]]:
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
        
        print(f"Debug - Has tool calls: {hasattr(response, 'tool_calls') and bool(response.tool_calls)}")
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"Debug - Tool calls: {response.tool_calls}")
            updated_state = {"messages": state.messages + [response]}
            next_node_name = NodeName.WEB_SEARCH
        else:
            updated_state = {"messages": state.messages + [response], "final_recommendation": response.content}
            next_node_name = NodeName.HUMAN_FEEDBACK
        
        return Command(update=updated_state, goto=next_node_name)
    
    return final_recommender
