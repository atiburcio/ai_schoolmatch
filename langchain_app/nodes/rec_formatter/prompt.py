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

    Analyses: {compatibility_analyses}

    Format the report in a clear, professional style suitable for investment banking presentation."""

HUMAN_MESSAGE = """{compatibility_analyses}"""