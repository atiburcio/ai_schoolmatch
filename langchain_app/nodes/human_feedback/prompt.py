SYSTEM_MESSAGE = """You will be provided with human feedback about the merger final recommendation.
If there is no feedback or if the user is satisfied (e.g., "looks good", "nice"), return None.
Focus on extracting specific points that need to be addressed in the next iteration of the recommendation."""

HUMAN_MESSAGE = """Previous recommendation:
{final_recommendation}

Human feedback:
{human_feedback_text}

Please analyze this feedback and provide a clear summary of what needs to be reconsidered or improved."""