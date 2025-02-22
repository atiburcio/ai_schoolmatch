from typing import Callable

from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_app.nodes.ipeds_semantic_search.prompt import HUMAN_MESSAGE, SYSTEM_MESSAGE

from models.state import State
from models.analysis_state import VectorDataBaseResults
from db.college_vector_store import CollegeVectorStore
from models.constants import SECTOR_MAP, PROGRAM_LEVELS


def _format_partner_info(metadata: dict[str, any], document: str) -> str:
    """Format partner institution information into a readable string.
    
    Args:
        metadata: Institution metadata from IPEDS
        document: Additional institution description
        
    Returns:
        Formatted string with institution information
    """
    sector = metadata.get('SECTOR')
    sector_text = SECTOR_MAP.get(sector, 'Unknown') if sector else 'Unknown'
    
    programs = [desc for level, desc in PROGRAM_LEVELS.items() 
               if metadata.get(level) == 1]
    
    return f"""
Institution: {metadata.get('INSTNM', 'Unknown')}
Location: {metadata.get('CITY', 'N/A')}, {metadata.get('STABBR', 'N/A')}
Type: {sector_text}
Programs Offered: {', '.join(programs) if programs else 'Information not available'}

Additional Information:
{document}
"""


def create_ipeds_semantic_search(vector_store: CollegeVectorStore, llm: ChatOpenAI) -> Callable[[State], State]:
    """Creates a node that finds semantic similarity between institutions.
    
    Args:
        vector_store: Vector store containing college embeddings
        llm: Language model for semantic search analysis
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with semantic search results
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    
    chain = prompt | llm
    
    def ipeds_semantic_search(state: State) -> State:
        """Returns semantically similar institutions to the target school."""
        try:
            if not state.features:
                print("Error: No features found in state")
                return state
            
            # Get more matches than needed since we'll filter some out
            matches = vector_store.find_similar_colleges(state.features, n_results=10)
            if not matches:
                print("No matches found in vector store")
                return state
            
            ipeds_semantic_search = []
            target_school = state.school.lower().strip()
            
            for match in matches:
                school_name = match['metadata'].get('INSTNM', '').lower().strip()
                
                # Skip if this is the target school
                if target_school in school_name or school_name in target_school:
                    continue
                
                partner_info = _format_partner_info(match['metadata'], match['document'])
                response: AIMessage = chain.invoke({
                    "features": state.features,
                    "partner_description": partner_info,
                    "run_name": "IPEDS Semantic Search Analysis",
                })
                
                ipeds_semantic_search.append(VectorDataBaseResults(
                    school=match['metadata'].get('INSTNM', 'Unknown Institution'),
                    location=f"{match['metadata'].get('CITY', 'N/A')}, {match['metadata'].get('STABBR', 'N/A')}",
                    analysis=response.content,
                    similarity_score=1.0 - match['distance']  # Convert distance to similarity
                ))
                
                # Only keep top 10 matches
                if len(ipeds_semantic_search) == 10:
                    break
            
            return State(
                school=state.school,
                features=state.features,
                ipeds_semantic_search=ipeds_semantic_search,
                recommendations=state.recommendations,
                final_recommendation=state.final_recommendation,
                messages=state.messages + [response]  # Add new message while preserving existing ones
            )
            
        except Exception as e:
            print(f"Error in IPEDS semantic search analyzer: {str(e)}")
            return State(
                school=state.school,
                features=state.features,
                ipeds_semantic_search=[],
                recommendations="",
                final_recommendation="",
                messages=state.messages  # Preserve existing messages
            )
    
    return ipeds_semantic_search
