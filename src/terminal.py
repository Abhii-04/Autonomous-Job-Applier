from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


console = Console()

class Terminal:
    def welcome(self):
        console.print(Panel.fit("[bold cyan]Welcome [/bold cyan]"))

    def user_input(self):
        return Prompt.ask("[bold blue]You: [/bold blue]")

    def bot_message(self,text):
        console.print(Panel(text, title="Bot",border_style="green"))

    def tool_message(self, tool, text):
        console.print(Panel(text, title=f"Tool: {tool}", border_style="blue"))

    
ui = Terminal()
ui.welcome()