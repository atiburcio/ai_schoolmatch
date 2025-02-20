SYSTEM_MESSAGE = """Extract M&A-relevant features for the target institution in these areas:
    1. Financial: Type (public/private), size/scope, key revenue programs, cost of tuition
    2. Academic: Programs, degrees, unique offerings
    3. Market: Location, demographics, online capabilities
    4. Culture: Mission, values, history

    Target: {school}
    
    Organize features concisely to help identify merger partners. Be specific and provide
    as much information as possible.
    """

HUMAN_MESSAGE = "Target school for feature extraction: {school}"