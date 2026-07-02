from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage, SystemMessage, ToolMessage


class ConversationSummaryMiddleware(AgentMiddleware):
    def __init__(self, model, keep_last: int = 6, max_tool_chars: int = 1000):
        self.model = model
        self.keep_last = keep_last
        self.max_tool_chars = max_tool_chars

    async def awrap_model_call(self, request, handler):
        summary = request.state.get("summary", "")

        if not summary:
            return await handler(request)

        return await handler(
            request.override(
                messages=[
                    SystemMessage(
                        content=f"Previous conversation summary:\n{summary}"
                    ),
                    *request.messages,
                ]
            )
        )

    def _message_to_text(self, message) -> str:
        role = getattr(message, "type", message.__class__.__name__)

        content = getattr(message, "content", "")

        if isinstance(content, list):
            content = "\n".join(
                str(item.get("text", item)) if isinstance(item, dict) else str(item)
                for item in content
            )

        content = str(content)

        if role == "human":
            return f"User: {content}"

        if role == "ai":
            # IMPORTANT:
            # Do NOT preserve tool_calls here.
            # Only summarize visible assistant text.
            return f"Assistant: {content}"

        if role == "tool":
            return f"Tool result: {content[:self.max_tool_chars]}"

        if role == "system":
            return f"System: {content}"

        return f"{role}: {content}"

    def _safe_delete_cutoff(self, messages) -> int:
        """Return a prefix cutoff that does not orphan ToolMessages."""
        cutoff = max(0, len(messages) - self.keep_last)

        while True:
            tool_call_parent: dict[str, int] = {}

            for index, message in enumerate(messages):
                if not isinstance(message, AIMessage):
                    continue

                for tool_call in getattr(message, "tool_calls", []) or []:
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        tool_call_parent[tool_call_id] = index

                for tool_call in getattr(message, "invalid_tool_calls", []) or []:
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        tool_call_parent[tool_call_id] = index

            adjusted_cutoff = cutoff

            for message in messages[cutoff:]:
                if not isinstance(message, ToolMessage):
                    continue

                parent_index = tool_call_parent.get(message.tool_call_id)
                if parent_index is not None and parent_index < adjusted_cutoff:
                    adjusted_cutoff = parent_index

            if adjusted_cutoff == cutoff:
                return cutoff

            cutoff = adjusted_cutoff

    def after_model(self, state, runtime):
        messages = state.get("messages", [])

        if len(messages) <= self.keep_last:
            return None

        cutoff = self._safe_delete_cutoff(messages)

        if cutoff <= 0:
            return None

        old_messages = messages[:cutoff]

        summary = state.get("summary", "")

        plain_text_history = "\n\n".join(
            self._message_to_text(m)
            for m in old_messages
        )

        if summary:
            prompt = f"""
You are updating a running conversation summary.

Existing summary:
{summary}

New conversation messages:
{plain_text_history}

Update the summary. Keep it concise, factual, and useful for continuing the task.
Do not include raw tool call IDs.
Do not include JSON tool_call structures.
"""
        else:
            prompt = f"""
Create a concise summary of this conversation so far.

Conversation messages:
{plain_text_history}

Keep only useful context needed to continue the task.
Do not include raw tool call IDs.
Do not include JSON tool_call structures.
"""

        response = self.model.invoke([
            SystemMessage(content="You summarize agent conversations safely."),
            HumanMessage(content=prompt),
        ])

        delete_messages = [
            RemoveMessage(id=m.id)
            for m in old_messages
            if getattr(m, "id", None)
        ]

        return {
            "summary": response.content,
            "messages": delete_messages,
        }
