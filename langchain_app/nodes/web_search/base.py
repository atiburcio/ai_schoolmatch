from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver

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

SKILLS_DIR = Path(__file__).resolve().parents[3] / "skills"


def create_web_search_tool_node() -> Callable[[State], State]:
    skill_path = SKILLS_DIR / "web-research" / "SKILL.md"
    skill_content = skill_path.read_text()

    skills_files = {
        "/skills/web-research/SKILL.md": skill_content,
    }

    checkpointer = MemorySaver()

    agent = create_deep_agent(
        tools=[tavily_web_search],
        skills=["./skills/"],
        checkpointer=checkpointer,
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

        result = agent.invoke(
            {
                "messages": [{"role": "user", "content": query}],
                "files": skills_files,
            },
            config={"configurable": {"thread_id": "web-search"}},
        )
        content = result["messages"][-1].content

        return {"messages": [AIMessage(content=f"Web Search Results:\n\n{content}")]}

    return web_search_with_state_update
