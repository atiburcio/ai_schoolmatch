from typing import Literal, Callable

from langgraph.types import Command, interrupt
from pydantic import BaseModel

from models.state import State, NodeName
from langchain_app.utils.human_feedback import (
    create_human_feedback_message_list,
    HUMAN_FEEDBACK_INPUT_MSG,
    EMPTY_INPUT_MSG,
)


def create_human_feedback_node(
) -> Callable[[State], Command[Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]]]:
    """
    Creates a node that prompts the user for feedback on the final recommendation.

    Returns:
        Callable: A function that takes a State and returns a Command 
                  with a Literal indicating the next node name.
    """

    human_feedback_func = create_get_human_feedback(
        messages_primary_key="messages",
        node_one_name=NodeName.FINAL_RECOMMENDER,
        node_no_feedback_name=NodeName.END,
    )

    def human_feedback_wrapper(
        state: State
    ) -> Command[Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]]:
        """
        Wrapper for human feedback node.

        Args:
            state (State): The current state.

        Returns:
            Command: The command to transition to the next node.
        """
        return human_feedback_func(state)

    return human_feedback_wrapper


def create_get_human_feedback(
    messages_primary_key: str,
    node_one_name: str,
    node_no_feedback_name: str,
) -> Callable[[BaseModel], Command]:
    """
    Creates a function that gets human feedback on the final recommendation,
    updates the state accordingly, and determines the next node.

    Args:
        messages_primary_key (str): Primary key for the messages list in the state.
        node_one_name (NodeName): Name of the node to go to if the user provides feedback.
        node_no_feedback_name (NodeName): Name of the node to go to if the user does not provide feedback.

    Returns:
        Callable: A function that takes a BaseModel state and returns a Command.
    """

    def get_human_feedback(state: BaseModel) -> Command:
        """
        Gets human feedback on the final recommendation.

        Args:
            state (BaseModel): State with the final recommendation.

        Returns:
            Command: The command to update state and transition to the next node.
        """
        human_feedback_text = interrupt(HUMAN_FEEDBACK_INPUT_MSG)
        if human_feedback_text == EMPTY_INPUT_MSG:
            return _get_command_for_no_feedback(node_no_feedback_name)

        updated_state = _get_updated_state(
            human_feedback_text,
            messages_primary_key,
            state,
        )
        next_node_name = _get_next_node_name(
            node_one_name,
        )
        return Command(update=updated_state, goto=next_node_name)

    return get_human_feedback


def _get_command_for_no_feedback(node_no_feedback_name: NodeName) -> Command:
    """
    Creates a command to transition to the 'no feedback' node.

    Args:
        node_no_feedback_name (NodeName): The node to transition to if no feedback is provided.

    Returns:
        Command: The command to transition to the 'no feedback' node.
    """
    return Command(goto=node_no_feedback_name)


def _get_updated_state(
    human_feedback_text: str,
    messages_primary_key: str,
    state: BaseModel
) -> dict:
    """
    Updates the state with the human feedback.

    Args:
        human_feedback_text (str): The feedback text provided by the user.
        messages_primary_key (str): The key for storing messages in the state.
        state (BaseModel): The current state containing existing messages.

    Returns:
        dict: A dictionary representing the updated state.
    """
    new_messages = create_human_feedback_message_list(human_feedback_text)
    existing_messages = getattr(state, messages_primary_key, [])
    return {
        messages_primary_key: existing_messages + new_messages,
    }


def _get_next_node_name(
    node_one_name: NodeName,
) -> NodeName:
    """
    Determines the next node name to navigate to.

    Args:
        node_one_name (NodeName): The node to transition to if feedback is provided.

    Returns:
        NodeName: The next node name.
    """
    return node_one_name