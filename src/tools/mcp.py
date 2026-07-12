from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from contextlib import asynccontextmanager
import os

NODE_BIN = "/home/abhishek/.nvm/versions/node/v22.23.1/bin"

PLAYWRIGHT_MCP_CONNECTIONS = {
    "playwright": {
        "transport": "stdio",
        "command": f"{NODE_BIN}/npx",
        "args": [
            "-y",
            "@playwright/mcp@latest",
            "--browser=chrome",
            "--user-data-dir=./browser-profile",
            "--image-responses=omit",
            "--snapshot-mode=none",
        ],
        "env": {
            **os.environ,
            "PATH": f"{NODE_BIN}:{os.environ.get('PATH', '')}",
            "DISPLAY": ":1",
            "XAUTHORITY": "/run/user/1000/gdm/Xauthority",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
        },
    }
}


@asynccontextmanager
async def get_mcp_tools():
    client = MultiServerMCPClient(
        PLAYWRIGHT_MCP_CONNECTIONS,
    )

    async with client.session("playwright") as session:
        yield await load_mcp_tools(session)
