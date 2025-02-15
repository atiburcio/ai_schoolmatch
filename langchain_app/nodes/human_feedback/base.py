from typing import Literal
from typing_extensions import Callable

from langgraph.types import Command, interrupt
from pydantic import BaseModel

from models.state import State
from models.state import NodeName
from langchain_app.utils.human_feedback import (
    create_human_feedback_message_list, HUMAN_FEEDBACK_INPUT_MSG, EMPTY_INPUT_MSG
)


def create_human_feedback_node(
) -> Callable[[State], Command[Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]]]:
    """Creates a node that prompts the user for feedback on the final recommendation.
    
    Returns:
        Callable that takes a State and returns a Command with a Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]
    """

    human_feedback_func = create_human_feedback(
        messages_primary_key = "final_recommendation"
        node_name = NodeName.FINAL_RECOMMENDER
        node_no_feedback = NodeName.END
    )

    def human_feedback_wrapper(state: State
    ) -> Command[Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]]:
        """Wrapper for human feedback node."""
        return human_feedback_func(state)
    
    return human_feedback_wrapper

def create_human_feedback(
    messages_primary_key: str,
    node_name: str,
    node_no_feedback_name: str,
) -> Callable[[BaseModel], Command]:
    """Creates a function that gets human feedback on the final recommendation.
    , updates the state accordingly and goes to the next node.
    
    Args:
        messages_primary_key: Primary key for the messages list in the state
        node_name: Name of the node to go to if the user provides feedback
        node_no_feedback: Name of the node to go to if the user does not provide feedback
    
    Returns:
        Callable that takes a State and returns a Command
    """

    def get_human_feedback(state: BaseModel) -> Command:
        """Gets human feedback on the final recommendation.
        
        Args:
            state: State with the final recommendation
        """
        human_feedback_text = interupt(HUMAN_FEEDBACK_INPUT_MSG)
        if human_feedback_text == EMPTY_INPUT_MSG:
            return _get_command_for_no_feedback(node_no_feedback_name)

        updated_state = 



def _get_command_for_no_feedback(node_no_feedback_name: str) -> Command:
    return Command(goto=node_no_feedback_name)