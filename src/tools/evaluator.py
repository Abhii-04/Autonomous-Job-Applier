from langchain.agents.middleware import AgentMiddleware
import requests
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, SystemMessage, ToolMessage


class evaluator(AgentMiddleware):
    def __init__(self,model,keep_last :int=6, max_tools_chrs : int=1000 ) :
        self.model = model
        self.keep_last = keep_last
        self.max_tools_chars = max_tools_chrs

    async def awrap_model_call(self, request, handler, ) :
        summary = requests.state.get["summary" : " "]

        if not summary:
            return await  handler(requests)

        return await handler(
            request.override(
                mesages = [
                    SystemMessage(
                        content =f"summary of previous conversations: \n{summary}"
                    ),
                    *request.messages
                ]
            )
        )


    