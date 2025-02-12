
from typing import Callable

from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_app.nodes.compatibility_analyzer.prompt import HUMAN_TEMPLATE, SYSTEM_TEMPLATE

from models import AnalysisState, CompatibilityAnalysis
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


def create_compatibility_analyzer(vector_store: CollegeVectorStore, llm: ChatOpenAI) -> Callable[[AnalysisState], AnalysisState]:
    """Creates a node that analyzes compatibility between institutions.
    
    Args:
        vector_store: Vector store containing college embeddings
        llm: Language model for compatibility analysis
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with compatibility analyses
    """

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE),
        HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE),
    ])
    
    chain = prompt | llm
    
    def compatibility_analyzer(state: AnalysisState) -> AnalysisState:
        """Analyze compatibility with potential partner institutions."""
        try:
            if not state.features:
                print("Error: No features found in state")
                return state
            
            # Get more matches than needed since we'll filter some out
            matches = vector_store.find_similar_colleges(state.features, n_results=10)
            if not matches:
                print("No matches found in vector store")
                return state
            
            compatibility_analyses = []
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
                    "run_name": "Compatibility Analysis",
                })
                
                compatibility_analyses.append(CompatibilityAnalysis(
                    school=match['metadata'].get('INSTNM', 'Unknown Institution'),
                    location=f"{match['metadata'].get('CITY', 'N/A')}, {match['metadata'].get('STABBR', 'N/A')}",
                    analysis=response.content,
                    similarity_score=1.0 - match['distance']
                ))
                
                # Stop once we have x unique institutions
                if len(compatibility_analyses) == 10:
                    break
            
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=compatibility_analyses,
                recommendations=state.recommendations,
                final_recommendation=state.final_recommendation
            )
            
        except Exception as e:
            print(f"Error in compatibility analyzer: {str(e)}")
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=[],
                recommendations=state.recommendations,
                final_recommendation=state.final_recommendation
            )
    
    return compatibility_analyzer