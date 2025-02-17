SYSTEM_MESSAGE = """ You will be provided with human feedback about node one.
Your task is the analyze the feedback and contextualize it.

If there is no feedback, please set the feedback to None.

If the users if happy with the recommendation by saying things like "looks good" or "nice", this
implies no changes are needed and the feedback can be set to None.
"""

HUMAN_MESSAGE = """Past human feedback:
{past_human_feedback_texts}

Text one:
{text_one}

Current human feedback:
{human_feedback_text}
"""