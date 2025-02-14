SYSTEM_MESSAGE = """Analyze the compatibility between the target institution and potential partners.
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
HUMAN_MESSAGE = """Target Features: {features}\nPotential Partner: {partner_description}"""