from langchain_core.tools import tool
from typing import Any , Callable
from langchain.agents.middleware import AgentMiddleware,AgentState,ModelRequest,ModelResponse


class RequestsLoggerMiddleware(AgentMiddleware):
    """logs all model requests for debugging"""
    def before_model(self,state:AgentState,runtime)->dict[str,Any] | None:
        """log before model exectution"""
        message_count = len(state.get("messages",[]))
        print(f"[BEFORE MODEL] processing {message_count} messages")
        return None

    async def awrap_model_call(self,request:ModelRequest,handler: Callable[[ModelRequest],ModelResponse]) -> ModelResponse:
        """ Logs the model requests details and call the handler """
        print(f"[MODEL REQUESTS]")
        print(f"Model: {request.model if hasattr(request,'model') else 'default'}")
        print(f"Tools available: {len(request.tools) if request.tools else 0}")

        response = await handler(request)
        print(f"[MODEL RESPONSE RECIEVED]")
        return response

    def after_model(self,state:AgentState,runtime) -> dict[str,Any] | None:
        """logs after model execution"""
        last_message = state["messages"][-1]
        if hasattr(last_message,'tool_calls') and last_message.tool_calls:
            print(f"[AFTER MODEL] Model requested {len(last_message.tool_calls)} tool call(s)")
        else:
            print(f"[AFTER MODEL] Model provided final response")
        return None  # Don't modify state