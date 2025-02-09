from typing import Dict, List, Optional
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from db.college_vector_store import CollegeVectorStore

def create_merger_feature_extractor(llm):
    """Creates a node that extracts M&A-relevant features from the target institution"""
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
    
    def feature_extractor(state):
        school = state["school"]
        response = chain.invoke({"school": school})
        return {"features": response.content}
    
    return feature_extractor

def create_compatibility_analyzer(vector_store: CollegeVectorStore, llm):
    """Creates a node that analyzes compatibility between institutions"""
    template = """Analyze compatibility between institutions:

    Key Factors:
    1. Strategic (40%): Market, programs, revenue, costs
    2. Cultural (30%): Mission, values, history, governance
    3. Operational (30%): Location, tech, accreditation, regulation

    Target: {features}
    Partner: {partner_description}

    Provide:
    1. Score (0-100)
    2. Key Synergies
    3. Challenges
    4. Risks"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "Target: {features}\nPartner: {partner_description}")
    ])
    
    chain = prompt | llm
    
    def compatibility_analyzer(state):
        features = state["features"]
        school_name = state["school"]  # Get the target school name
        
        # Get more matches than needed since we'll filter some out
        matches = vector_store.find_similar_colleges(features, n_results=20)
        
        # Keep track of schools we've seen to avoid duplicates
        seen_schools = set()
        filtered_matches = []
        
        for match in matches:
            school = match["metadata"]["name"]
            # Only add schools we haven't seen before and that aren't the target school
            if (school.lower() not in seen_schools and 
                school_name.lower() not in school.lower()):
                filtered_matches.append(match)
                seen_schools.add(school.lower())
            
            # Stop once we have 5 unique schools
            if len(filtered_matches) == 5:
                break
        
        analyses = []
        for match in filtered_matches:
            response = chain.invoke({
                "features": features,
                "partner_description": match["metadata"]["name"]
            })
            analyses.append({
                "partner": match["metadata"]["name"],
                "analysis": response.content
            })
        
        return {"compatibility_analyses": analyses}
    
    return compatibility_analyzer

def create_merger_recommendation_formatter(llm):
    """Creates a node that formats merger recommendations"""
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
    
    def recommendation_formatter(state):
        analyses = state["compatibility_analyses"]
        response = chain.invoke({"compatibility_analyses": str(analyses)})
        return {"recommendations": response.content}
    
    return recommendation_formatter

def create_final_recommender(llm):
    template = """Based on the compatibility analyses, provide a final recommendation with:

    1. Executive Summary
    - Top partners and scores
    - Key recommendation
    
    2. Analysis
    - Strategic alignment
    - Cultural fit
    - Operations
    
    3. Risks & Mitigation
    
    4. Next Steps
    - Actions
    - Timeline
    - Stakeholders
    
    5. Financial Impact
    - Synergies
    - Costs
    - ROI timeline
    
    6. Conclusion
    - Final choice
    - Success factors"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{recommendations}")
    ])
    
    chain = prompt | llm
    
    def recommendation_formatter(state):
        recommendations = state.get("recommendations", "")
        response = chain.invoke({"recommendations": recommendations})
        return {"final_recommendation": response.content}
    
    return recommendation_formatter
