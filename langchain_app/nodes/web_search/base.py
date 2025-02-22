from typing import Callable
from langchain.prompts.chat import (
    ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from models.state import State, SearchQuery
from langchain_app.nodes.web_search.prompt import SYSTEM_MESSAGE, HUMAN_MESSAGE

SEARCH_ANALYSIS_SYSTEM = """You are an expert at analyzing educational institutions for M&A purposes.
Given web search results about a target institution, extract relevant information to enhance our understanding
in these key areas:

1. Financial: Assets, endowment, revenue streams, debt
2. Academic: Programs, degrees, unique offerings
3. Market: Location, tuition costs, online capabilities
4. Culture: Mission, values, history
5. Demographics: Race/ethnicity, gender
6. Technology: Infrastructure, online capabilities, computing resources

Current Features:
{features}

Web Search Results:
{search_results}

Analyze the search results and enhance the current features with any new, factual information found.
Format your response as a complete, updated feature set that includes both the original information
and any new information from the search results. Maintain the same structure and organization as the
original features.

Only include factual, verifiable information. If information conflicts with the current features,
note both pieces of information and their sources.

Use numbered sources in your report (e.g., [1], [2]) based on information from source documents
        
In the Sources section:
- Include all sources used in your report
- Provide full links to relevant websites or specific document paths
- Separate each source by a newline. Use two spaces at the end of each line to create a newline in Markdown.
- It will look like:

### Sources
[1] Link or Document name
[2] Link or Document name

7. Be sure to combine sources. For example this is not correct:

[3] https://ai.meta.com/blog/meta-llama-3-1/
[4] https://ai.meta.com/blog/meta-llama-3-1/

There should be no redundant sources. It should simply be:

[3] https://ai.meta.com/blog/meta-llama-3-1/

"""

SEARCH_ANALYSIS_HUMAN = """Current features:
{features}

Search results:
{search_results}"""

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
    tavily_search = TavilySearchResults(max_results=5)
    
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
