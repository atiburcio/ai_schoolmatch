from typing import Callable

from langchain.prompts.chat import (
    ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from models.state import State, SearchQuery
from langchain_app.nodes.web_search.prompt import SYSTEM_MESSAGE, HUMAN_MESSAGE
from langchain_app.nodes.web_search.search_analysis_prompt import (
    SYSTEM_MESSAGE as SEARCH_ANALYSIS_SYSTEM, HUMAN_MESSAGE as SEARCH_ANALYSIS_HUMAN
)

@tool
def create_web_search(llm: ChatOpenAI) -> Callable[[State], State]:
    """Creates a node that performs web searches to enhance feature information.
    
    Args:
        llm: Language model for generating search queries
        
    Returns:
        Callable that takes a State and returns updated state with enhanced features
    """
    # Create prompt for generating search queries
    query_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    
    # Create prompt for analyzing search results
    analysis_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SEARCH_ANALYSIS_SYSTEM),
        HumanMessagePromptTemplate.from_template(SEARCH_ANALYSIS_HUMAN),
    ])
    
    # Create chains and tools
    query_chain = query_prompt | llm
    analysis_chain = analysis_prompt | llm
    tavily_search = TavilySearchResults(max_results=10)
    
    def web_search(state: State) -> State:
        """Enhance features with web search results."""
        try:
            # Generate search query based on current features
            query_response: AIMessage = query_chain.invoke({
                "school": state.school,
                "run_name": "Web Search Query Generation"
            })
            
            # Use the generated query to search using Tavily
            search_query = SearchQuery(search_query=query_response.content)
            search_results = tavily_search.invoke(search_query.search_query)
            
            # Format search results for analysis
            formatted_results = "\n\n---\n\n".join(
                [
                    f'Source: {doc["url"]}\n{doc["content"]}'
                    for doc in search_results
                ]
            )
            
            # Analyze search results and enhance features
            analysis_response: AIMessage = analysis_chain.invoke({
                "features": state.features,
                "search_results": formatted_results,
                "run_name": "Web Search Analysis"
            })
            
            # Return updated state with enhanced features
            return State(
                school=state.school,
                features=analysis_response.content,
                ipeds_semantic_search=state.ipeds_semantic_search,
                recommendations=state.recommendations,
                final_recommendation=state.final_recommendation,
                messages=state.messages + [query_response, analysis_response]
            )
            
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return state
    
    return web_search
