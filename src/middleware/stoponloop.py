from typing import Annotated
from typing_extensions import NotRequired

from langchain.agents.middleware import AgentState, AgentMiddleware
from langchain_core.messages import ToolMessage


def sum_counts(old: int | None, new: int | None) -> int:
    return (old or 0) + (new or 0)


class CustomState(AgentState):
    tool_count: Annotated[NotRequired[int], sum_counts]


class RepetativeToolCall(AgentMiddleware):
    state_schema = CustomState

    async def awrap_tool_call(self, request, handler):
        tool_messages = [
            m for m in request.state.get("messages", [])
            if isinstance(m, ToolMessage)
        ]

        current_tool_name = request.tool_call.get("name")
        current_tool_call_id = request.tool_call.get("id")

        if tool_messages:
            previous_tool = tool_messages[-1]

            if previous_tool.name == current_tool_name:
                return ToolMessage(
                    content=f"Blocked repeated tool call: {current_tool_name}",
                    name=current_tool_name,
                    tool_call_id=current_tool_call_id,
                )

        response = await handler(request)

        return response