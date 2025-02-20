from langchain_app.nodes.final_rec.prompt import HUMAN_MESSAGE


SYSTEM_MESSAGE = """Based on the compatibility analyses, create a detailed M&A recommendation report.
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

    You will receive a list of compatibility analyses. Each analysis contains:
    - school: The name of the potential partner institution
    - location: The city and state of the institution
    - analysis: Detailed compatibility analysis
    - similarity_score: A score from 0 to 1 indicating similarity

    Create a section for EACH school in the analyses, ordered by similarity score in descending order.
    Use the school name as the section header.

    Analyses: {compatibility_analyses}

    Format the report in a clear, professional style suitable for investment banking presentation.
    Provide as much information as possible, using the data provided in the analyses.
    A managing director will be reviewing the report who is an expert in the field. 
    """

HUMAN_MESSAGE = """{compatibility_analyses}"""