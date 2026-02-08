from __future__ import annotations

import logging
from typing import Callable

from langchain_core.messages import AIMessage

from models.state import State

logger = logging.getLogger(__name__)

try:
    from deepagents import create_deep_agent
    from deepagents_cli.tools import web_search as tavily_web_search
except ImportError as e:
    raise ImportError(
        "deepagents is required for the web search node. "
        "Install it with: pip install deepagents"
    ) from e


def create_web_search_tool_node() -> Callable[[State], State]:
    agent = create_deep_agent(
        system_prompt=(
            "You are a web research agent for higher-education institution due diligence. "
            "When given a search query, use the web_search tool to gather recent, relevant facts. "
            "Synthesize results into concise bullet points and include source URLs."
        ),
        tools=[tavily_web_search],
    )

    def web_search_with_state_update(state: State) -> State:
        query = None

        for message in reversed(state.messages):
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.get("name") == "web_search":
                        query = tool_call.get("args", {}).get("query")
                        break
                break

        if not query:
            query = f"general information about {state.school}" if state.school else "general information about the school"
            logger.warning("No web_search tool call found in messages; falling back to query: %s", query)

        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        content = result["messages"][-1].content

        return {"messages": [AIMessage(content=f"Web Search Results:\n\n{content}")]}

    return web_search_with_state_update
