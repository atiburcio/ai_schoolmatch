from langchain_core.messages import HumanMessage

HUMAN_FEEDBACK_INPUT_MSG = "Please provide feedback on the final recommendation: "

EMPTY_INPUT_MSG = "__empty_input_msg__"

def create_human_feedback_message_list(human_feedback_text: str) -> list[HumanMessage]:
    """Creates a list of HumanMessages from the human feedback text.
    
    Args:
        human_feedback_text: Text from the human feedback
    """
    return (
        [HumanMessage(content=f"Human feedback: {human_feedback_text}")]
        if human_feedback_text
        else []
    )