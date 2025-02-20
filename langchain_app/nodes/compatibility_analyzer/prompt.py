SYSTEM_MESSAGE = """Analyze the compatibility between the target institution and potential partners.
    Consider these factors in order of importance:

    1. Strategic Fit:
        - Market expansion opportunities
        - Program portfolio complementarity

    2. Cultural Alignment:
        - Mission statement compatibility
        - Shared values and educational philosophy
        - Historical focus and tradition
        - Governance structure compatibility

    3. Operational Feasibility:
        - Geographic proximity/overlap
        - Technology infrastructure compatibility
        - Accreditation requirements
        - Regulatory considerations
        - Student body demographics

    4. Financial Feasibility:  
        - Price of tuition and fees (in-state/out-of-state)
        - Financial aid availability
        - Financial aid acceptance rate

    Target Features: {features}
    Potential Partner: {partner_description}

    Provide a structured analysis of the compatibility, including:
    1. Compatibility Score (0-100)
    2. Key Synergies
    3. Potential Challenges
    4. Risk Factors
    """
HUMAN_MESSAGE = """Target Features: {features}\nPotential Partner: {partner_description}"""