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
    template = """Given the following compatibility analyses and recommendations, provide a final recommendation for the merger.
    
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
    
    def recommendation_formatter(state):
        recommendations = state.get("recommendations", "")
        response = chain.invoke({"recommendations": recommendations})
        return {"final_recommendation": response.content}
    
    return recommendation_formatter
