SYSTEM_MESSAGE = """Extract key M&A-relevant features from the target institution based on the provided description and IPEDS data.
Focus on these key areas:
    1. Financial: Assets, endowment, revenue streams, debt
    2. Academic: Programs, degrees, unique offerings
    3. Market: Location, tuition costs, online capabilities
    4. Culture: Mission, values, history
    5. Demographics: Race/ethnicity, gender
    6. Technology: Infrastructure, online capabilities, computing resources

    Target School: {school}
    Target School Description: {description}
    IPEDS Data: {ipeds_data}
    
    Extract and organize the key features from both the description and IPEDS data. Be specific and include
    as much information as possible. Do not make up information; instead, refer to the
    original source for context. If information is not available from either source,
    state "Information not available" for that section.
    """

HUMAN_MESSAGE = """Target School: {school}
Description: {description}
IPEDS Data: {ipeds_data}"""