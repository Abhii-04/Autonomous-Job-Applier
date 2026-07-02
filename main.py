from src.agent import BrowserAgentRuntime
import os 
from dotenv import load_dotenv
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


DEFAULT_TASK = "open naukri.com."

console = Console()

class Terminal:
    def __init__(self):
        self.console = Console()

    def welcome(self):
        console.print(Panel.fit("[bold cyan]Welcome [/bold cyan]"))

    def user_input(self):
        return Prompt.ask("[bold blue]You: [/bold blue]")

    def bot_message(self,text):
        console.print(Panel(text, title="Bot",border_style="green"))

    def tool_message(self, tool, text):
        console.print(Panel(text, title=f"Tool: {tool}", border_style="blue"))

    def status(self, text):
        self.console.print(f"[cyan]{text}...[/cyan]")
    



async def main():
    async with BrowserAgentRuntime() as runtime:
        ui = Terminal()
        ui.welcome()
        while True:
            task = Prompt.ask("\n[bold yellow]You[/bold yellow]")
            if not task:
                task = DEFAULT_TASK

            if task.lower() in ["exit", "quit"]:
                ui.bot_message("Exiting")
                break

            ui.status("Agent is thinking")

            result = await runtime.run(task)
            final_message = result["messages"][-1].content
            ui.bot_message(final_message)

if __name__ == "__main__":
    asyncio.run(main())
