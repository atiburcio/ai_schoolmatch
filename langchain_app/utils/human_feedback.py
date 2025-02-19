from langchain_core.messages import HumanMessage
from typing import Union, List, Any

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

def extract_feedback_history(messages: List[Any]) -> str:
    """Extracts all human feedback from messages in chronological order.
    
    Args:
        messages: List of messages that may contain human feedback
        
    Returns:
        str: All human feedback messages joined with newlines, or "No feedback provided" if none found
    """
    feedback_texts = []
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            content = msg.content.replace("Human feedback: ", "")
            feedback_texts.append(content)
        elif isinstance(msg, dict) and msg.get("role") == "human":
            content = msg.get("content", "").replace("Human feedback: ", "")
            feedback_texts.append(content)
    
    return "\n".join(feedback_texts) if feedback_texts else "No feedback provided"