from src.tools.bash import bash
from src.middleware.localcontext import ConversationSummaryMiddleware
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

import os 
from dotenv import load_dotenv

from deepagents import create_deep_agent, FilesystemPermission
from pydantic import BaseModel
from typing import List,Any,Optional
from pathlib import Path
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
from src.prompt import applier_prompt, orchestrator_prompt,Evaluator_prompt
from src.middleware.stoponloop import RepetativeToolCall
import uuid
from deepagents.backends.filesystem import FilesystemBackend
from src.tools.mcp import get_mcp_tools


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



def orchestrator(tools:List):
    
    return create_deep_agent(
        model = llm,
        tools = tools ,
        system_prompt=orchestrator_prompt,
        skills = [SKILLS_DIR],
        checkpointer = checkpointer,       #short term memory
        # memory = ["memory/AGENT.md"],      #Long term memory
        backend=FilesystemBackend(root_dir = PROJECT_ROOT,virtual_mode=True),
        store=store,
        middleware=[
            # ConversationSummaryMiddleware(model=llm, keep_last=8),
            RepetativeToolCall(),
            ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=100000,
                    keep=5,
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
                "description": "use this tool  to peform all web related tasks such as web automation etc",
                "system_prompt":applier_prompt,
                "tools" : tools
            },
            {
                "name" : "evaluator",
                "description": "use this tool to evaluate the worker's performance",
                "system_prompt":Evaluator_prompt,
                "tools" : [bash],
                "middleware":[ConversationSummaryMiddleware(model=llm, keep_last=8),
                ]
            }
        ]
    )


class BrowserAgentRuntime:
    async def __aenter__(self):
        self._mcp_tools_context = get_mcp_tools()
        mcp_tools = await self._mcp_tools_context.__aenter__()
        tools = [ *mcp_tools]
        self.agent = orchestrator(tools)
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
