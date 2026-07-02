from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from contextlib import asynccontextmanager


PLAYWRIGHT_MCP_CONNECTIONS = {
    "playwright": {
        "transport": "stdio",
        "command": "npx",
        "args": [
            "-y",
            "@playwright/mcp@latest",
            "--browser=chrome",
            "--user-data-dir=./browser-profile",
            "--output-dir=./reports",
            "--save-session",
            "--shared-browser-context",
            "--image-responses=omit",
            "--snapshot-mode=none",
        ],
        "env": {
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
