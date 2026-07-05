from typing import Callable
from langchain.agents.middleware import (
    wrap_tool_call,
    AgentState,
    AgentMiddleware,
    ModelRequest,
    ModelResponse
)
from langgraph.types import Command
from typing_extensions import NotRequired
from langchain_core.messages import ToolMessage

class CustomState(AgentState):
    """Agent state with tool_call tracking"""
    tool_messages :NotRequired[str]
    tool_count : NotRequired[int]

class RepetativeToolCall(AgentMiddleware):
    state_schema = CustomState
    

    async def awrap_tool_call(self,request,handler):
        tool_messages = [
            m for m in request.state["messages"]
            if isinstance(m,ToolMessage)
        ]

        if len(tool_messages) >=2:
            previous_tool = tool_messages[-1]
            two_previous_tool = tool_messages[-2]

            if previous_tool.name == two_previous_tool.name:
                return ToolMessage(
                    content = f"Blocked repeated tool call: {previous_tool.name}",
                    tool_call_id = request.tool_call("id")
                )
        response = await handler(request)

        old_count = request.state.get("tool_count",0)

        return Command(
            update = {
                "messages":[response],
                "tool_count" : old_count+1
            }
        )