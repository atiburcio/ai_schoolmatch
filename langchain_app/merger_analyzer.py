"""
Merger Analysis Module

This module provides functionality for analyzing potential mergers between educational institutions.
It uses LangChain for natural language processing and ChromaDB for vector similarity search.
"""

from typing import Dict, List, Optional, Any, Callable
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from db.college_vector_store import CollegeVectorStore
from models import AnalysisState, CompatibilityAnalysis

__all__ = [
    'create_feature_extractor',
    'create_compatibility_analyzer',
    'create_recommendation_formatter',
    'create_final_recommender'
]

# Constants for sector and program level mappings
SECTOR_MAP = {
    1: "Public, 4-year or above",
    2: "Private nonprofit, 4-year or above",
    3: "Private for-profit, 4-year or above",
    4: "Public, 2-year",
    5: "Private nonprofit, 2-year",
    6: "Private for-profit, 2-year",
    7: "Public, less than 2-year",
    8: "Private nonprofit, less than 2-year",
    9: "Private for-profit, less than 2-year"
}

PROGRAM_LEVELS = {
    'LEVEL1': 'Less than one year certificate',
    'LEVEL2': 'One but less than two years certificate',
    'LEVEL3': "Associate's degree",
    'LEVEL4': 'Two but less than 4 years certificate',
    'LEVEL5': "Bachelor's degree",
    'LEVEL6': 'Postbaccalaureate certificate',
    'LEVEL7': "Master's degree",
    'LEVEL8': 'Post-master\'s certificate',
    'LEVEL17': 'Doctor\'s degree - research/scholarship',
    'LEVEL18': 'Doctor\'s degree - professional practice',
    'LEVEL19': 'Doctor\'s degree - other'
}

def create_feature_extractor(llm: ChatOpenAI) -> Callable[[AnalysisState], AnalysisState]:
    """Creates a node that extracts M&A-relevant features from the target institution.
    
    Args:
        llm: Language model for feature extraction
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with extracted features
    """
    template = """Extract M&A-relevant features for the target institution in these areas:
    1. Financial: Type (public/private), size/scope, key revenue programs
    2. Academic: Programs, degrees, unique offerings
    3. Market: Location, demographics, online capabilities
    4. Culture: Mission, values, history

    Target: {school}
    
    Organize features concisely to help identify merger partners."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{school}")
    ])
    
    chain = prompt | llm
    
    def feature_extractor(state: AnalysisState) -> AnalysisState:
        """Extract features from the school description."""
        try:
            response = chain.invoke({"school": state.school})
            return AnalysisState(
                school=state.school,
                features=response.content,
                compatibility_analyses=[],
                recommendations="",
                final_recommendation=""
            )
        except Exception as e:
            print(f"Error in feature extractor: {str(e)}")
            return AnalysisState(school=state.school)
    
    return feature_extractor

def format_partner_info(metadata: Dict[str, Any], document: str) -> str:
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
    template = """Analyze the compatibility between the target institution and potential partners.
    Consider these factors in order of importance:

    1. Strategic Fit (40% weight):
        - Market expansion opportunities
        - Program portfolio complementarity
        - Revenue synergy potential
        - Cost efficiency opportunities

    2. Cultural Alignment (30% weight):
        - Mission statement compatibility
        - Shared values and educational philosophy
        - Historical focus and tradition
        - Governance structure compatibility

    3. Operational Feasibility (30% weight):
        - Geographic proximity/overlap
        - Technology infrastructure compatibility
        - Accreditation requirements
        - Regulatory considerations

    Target Features: {features}
    Potential Partner: {partner_description}

    Provide a structured analysis of the compatibility, including:
    1. Compatibility Score (0-100)
    2. Key Synergies
    3. Potential Challenges
    4. Risk Factors
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "Target Features: {features}\nPotential Partner: {partner_description}")
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
                
                partner_info = format_partner_info(match['metadata'], match['document'])
                response = chain.invoke({
                    "features": state.features,
                    "partner_description": partner_info
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

def create_recommendation_formatter(llm: ChatOpenAI) -> Callable[[AnalysisState], AnalysisState]:
    """Creates a node that formats merger recommendations.
    
    Args:
        llm: Language model for formatting recommendations
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with formatted recommendations
    """
    template = """Based on the compatibility analyses, create a detailed M&A recommendation report.
    For each potential partner, include:

    1. Executive Summary
        - Partner overview
        - Strategic rationale
        - Key financial considerations

    2. Compatibility Analysis
        - Strategic fit assessment
        - Cultural alignment evaluation
        - Operational synergies

    3. Risk Assessment
        - Integration challenges
        - Regulatory considerations
        - Financial risks

    4. Next Steps
        - Due diligence priorities
        - Key stakeholder considerations
        - Timeline recommendations

    Analyses: {compatibility_analyses}

    Format the report in a clear, professional style suitable for investment banking presentation."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{compatibility_analyses}")
    ])
    
    chain = prompt | llm
    
    def recommendation_formatter(state: AnalysisState) -> AnalysisState:
        """Format recommendations based on compatibility analyses."""
        try:
            response = chain.invoke({"compatibility_analyses": str([analysis.model_dump() for analysis in state.compatibility_analyses])})
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations=response.content,
                final_recommendation=state.final_recommendation
            )
        except Exception as e:
            print(f"Error in recommendation formatter: {str(e)}")
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations="",
                final_recommendation=state.final_recommendation
            )
    
    return recommendation_formatter

def create_final_recommender(llm: ChatOpenAI) -> Callable[[AnalysisState], AnalysisState]:
    """Creates a node that makes the final recommendation.
    
    Args:
        llm: Language model for final recommendation
        
    Returns:
        Callable that takes an AnalysisState and returns updated state with final recommendation
    """
    template = """You are an expert investment banker who specializes in merger and acquisition (M&A) decisions. Given the following compatibility analyses and recommendations, provide a final recommendation for the merger.
    
    {recommendations}
    
    Please provide a structured analysis with the following sections:
    
    1. Executive Summary
    - Brief overview of the top recommended partner(s)
    - Key compatibility scores
    - High-level recommendation
    
    2. Compatibility Analysis
    - Analysis of strategic fit
    - Cultural alignment assessment
    - Operational synergies
    
    3. Risk Assessment
    - Key risks identified
    - Potential mitigation strategies
    
    4. Next Steps
    - Recommended immediate actions
    - Timeline considerations
    - Key stakeholders to involve
    
    5. Financial Considerations
    - Potential synergies and cost savings
    - Investment requirements
    - Expected ROI timeline
    
    6. Closing Remarks
    - Final recommendation
    - Critical success factors
    
    Format the report in a clear, professional style suitable for investment banking presentation."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{recommendations}")
    ])
    
    chain = prompt | llm
    
    def final_recommender(state: AnalysisState) -> AnalysisState:
        """Generate final recommendation based on all analyses."""
        try:
            response = chain.invoke({"recommendations": state.recommendations})
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations=state.recommendations,
                final_recommendation=response.content
            )
        except Exception as e:
            print(f"Error in final recommender: {str(e)}")
            return AnalysisState(
                school=state.school,
                features=state.features,
                compatibility_analyses=state.compatibility_analyses,
                recommendations=state.recommendations,
                final_recommendation=""
            )
    
    return final_recommender
