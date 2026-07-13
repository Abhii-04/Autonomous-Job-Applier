from src.tools.bash import bash
from src.tools.mcp import get_mcp_tools

from src.middleware.localcontext import ConversationSummaryMiddleware
from src.middleware.logger import RequestsLoggerMiddleware
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

import os 
from dotenv import load_dotenv

from deepagents import create_deep_agent, FilesystemPermission
from pydantic import BaseModel
from typing import List,Any,Optional,Sequence
from pathlib import Path
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
from src.prompt import applier_prompt, orchestrator_prompt
from src.middleware.stoponloop import RepetativeToolCall
import uuid
from deepagents.backends.filesystem import FilesystemBackend

from langchain_core.tools import BaseTool

load_dotenv(override=True)

llm = ChatOpenAI(
    api_key = os.getenv('DEEPSEEK_API_KEY'),
    model = 'deepseek-v4-flash',
    base_url = 'https://api.deepseek.com'
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = "/skills"

checkpointer = InMemorySaver()
store = InMemoryStore()



def orchestrator(orchestrator_tool: Sequence[BaseTool],applier_tools: Sequence[BaseTool]):
    
    return create_deep_agent(
        model = llm,
        tools = orchestrator_tool ,
        system_prompt=orchestrator_prompt,
        checkpointer = checkpointer,
        backend=FilesystemBackend(root_dir = PROJECT_ROOT,virtual_mode=True),
        store=store,
        skills = [SKILLS_DIR],
        middleware=[
            # ConversationSummaryMiddleware(model=llm, keep_last=8),
            RequestsLoggerMiddleware(),
            RepetativeToolCall(),
            ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=10000,
                    keep=2,
                ),
            ],
        ),
        ],
        interrupt_on={
            "submit": True,
        },
        permissions=[
            FilesystemPermission(
                operations= ["read","write"],
                paths = ["/reports/"],
                mode="allow",
            )
        ],
        subagents = [
            {
                "name" : "applier",
                "description": (
                    "Use only when a job application form is already open in the "
                    "current browser tab. Fill fields, upload the resume, and prepare "
                    "the application. Do not search for jobs or reopen job links."
                ),
                "system_prompt":applier_prompt,
                "tools" : applier_tools,
                "skills" : [SKILLS_DIR],
                "middleware":[ConversationSummaryMiddleware(model=llm, keep_last=8),
                ]
            },
            
        ]
    )


ORCHESTRATOR_ALLOWED_TOOLS = {
    "browser_navigate",
    "browser_tabs",
    "browser_close",
    "browser_snapshot",
    "browser_click",
    "browser_wait_for",
}

APPLIER_ALLOWED_TOOLS = {
    "browser_navigate",
    "browser_snapshot",
    "browser_click",
    "browser_hover",
    "browser_type",
    "browser_fill_form",
    "browser_find",
    "browser_file_upload",
    "browser_select_option",
    "browser_press_key",
    "browser_wait_for",
}

class BrowserAgentRuntime:
    async def __aenter__(self):
        self._mcp_tools_context = get_mcp_tools()
        mcp_tools = await self._mcp_tools_context.__aenter__()
        all_mcp_tools = [ *mcp_tools]
        orchestrator_tools = [
            tool
            for tool in all_mcp_tools
            if tool.name in ORCHESTRATOR_ALLOWED_TOOLS
        ]
        applier_tools = [
            tool
            for tool in all_mcp_tools
            if tool.name in APPLIER_ALLOWED_TOOLS
        ]
        self.agent = orchestrator(orchestrator_tools,applier_tools)
        self.config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return await self._mcp_tools_context.__aexit__(exc_type, exc, traceback)

    async def run(self, task: str):
        return await self.agent.ainvoke({
            "messages":[
                {
                    "role":"user",
                    "content":task,
                }
            ]
        },config = self.config
        )


async def run_agent(task:str):
    async with BrowserAgentRuntime() as runtime:
        return await runtime.run(task)
