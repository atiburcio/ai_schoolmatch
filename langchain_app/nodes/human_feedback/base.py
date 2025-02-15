from typing import Literal
from langchain_openai import ChatOpenAI
from typing_extensions import Callable

from langgraph.types import Command, interrupt
from pydantic import BaseModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableSequence

from models.state import State
from models.state import NodeName
from langchain_app.utils.human_feedback import (
    create_human_feedback_message_list, HUMAN_FEEDBACK_INPUT_MSG, EMPTY_INPUT_MSG
)
from models.state import HumanFeedbackSeparation


def create_human_feedback_node(
) -> Callable[[State], Command[Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]]]:
    """Creates a node that prompts the user for feedback on the final recommendation.
    
    Returns:
        Callable that takes a State and returns a Command with a Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]
    """

    human_feedback_func = create_get_human_feedback(
        messages_primary_key = "final_recommendation",
        messages_node_one_key = "final_recommendation_with_feedback",
        node_one_name = NodeName.FINAL_RECOMMENDER,
        node_no_feedback_name = NodeName.END,
    )

    def human_feedback_wrapper(state: State
    ) -> Command[Literal[NodeName.FINAL_RECOMMENDER, NodeName.END]]:
        """Wrapper for human feedback node."""
        return human_feedback_func(state)
    
    return human_feedback_wrapper

# TODO: later, if we need to separate humand feedback to more than one node, we do that here.
def create_get_human_feedback(
    messages_primary_key: str,
    messages_node_one_key: str,
    node_one_name: str,
    node_no_feedback_name: str,
) -> Callable[[BaseModel], Command]:
    """Creates a function that gets human feedback on the final recommendation.
    , updates the state accordingly and goes to the next node.
    
    Args:
        messages_primary_key: Primary key for the messages list in the state
        node_one_name: Name of the node to go to if the user provides feedback
        node_no_feedback_name: Name of the node to go to if the user does not provide feedback
    
    Returns:
        Callable that takes a State and returns a Command
    """

    def get_human_feedback(state: BaseModel) -> Command:
        """Gets human feedback on the final recommendation.
        
        Args:
            state: State with the final recommendation
        """
        human_feedback_text = interrupt(HUMAN_FEEDBACK_INPUT_MSG)
        if human_feedback_text == EMPTY_INPUT_MSG:
            return _get_command_for_no_feedback(node_no_feedback_name)

        human_feedback_separation = _separate_human_feedback(
            state,
            human_feedback_text,
            messages_primary_key,
            messages_node_one_key
        )
        if not human_feedback_separation.has_feedback:
            return _get_command_for_no_feedback(node_no_feedback_name)

        updated_state = _get_updated_state(
            human_feedback_text, 
            human_feedback_separation,
            messages_primary_key,
            messages_node_one_key
        )

        next_node_name = _get_next_node_name(
            human_feedback_separation,
            node_one_name,
        )

        return Command(update=updated_state, goto=next_node_name)
    
    return get_human_feedback

def _separate_human_feedback(
    state: State,
    human_feedback_text: str,
    messages_primary_key:str,
    messages_node_one_key: str
) -> HumanFeedbackSeparation:
    past_human_feedback_texts = "\n".join(
        msg.content for msg in getattr(state, messages_primary_key) if isinstance(msg, HumanMessage)
    )

    separator_runnable = _create_human_feedback_separator_runnable()
    last_message_from_one: AIMessage = getattr(state, messages_node_one_key)[-1]
    human_feedback_separation = separator_runnable.invoke({
        "past_human_feedback_texts": past_human_feedback_texts,
        "last_message_from_one": last_message_from_one.content,
        "human_feedback_text": human_feedback_text,
    },
    {"run_name": "Human Feedback Separator"},
    )

    return human_feedback_separation


def _create_human_feedback_separator_runnable() -> RunnableSequence:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
        HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
    ])
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    llm_structured_output = llm.with_structured_output(HumanFeedbackSeparation)

    return prompt | llm_structured_output


def _get_command_for_no_feedback(node_no_feedback_name: str) -> Command:
    return Command(goto=node_no_feedback_name)


def _get_updated_state(
    human_feedback_text: str, 
    human_feedback_separation: HumanFeedbackSeparation,
    messages_primary_key:str,
    messages_node_one_key: str
) -> dict:
    messages_for_primary_key = create_human_feedback_message_list(human_feedback_text)
    messages_for_node_one_key = create_human_feedback_message_list(
        human_feedback_separation.feedback
    )
    return {
        messages_primary_key: messages_for_primary_key,
        messages_node_one_key: messages_for_node_one_key
    }


def _get_next_node_name(
    human_feedback_separation: HumanFeedbackSeparation,
    node_one_name: str,
) -> str:
    if human_feedback_separation.feedback:
        return node_one_name
    raise ValueError("Human feedback was not provided")