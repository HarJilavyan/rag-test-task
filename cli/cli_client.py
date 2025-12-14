import os
import requests
from rich.console import Console
from rich.prompt import Prompt

console = Console()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def main():
    console.print("[bold green]CLI client (calls backend API)[/bold green]")
    console.print(f"Backend: {BACKEND_URL}")
    console.print("Type 'exit' to quit.\n")

    while True:
        q = Prompt.ask("[bold cyan]You[/bold cyan]")
        if q.strip().lower() in {"exit", "quit"}:
            break

        resp = requests.post(f"{BACKEND_URL}/ask", json={"question": q}, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        console.print("\n[bold magenta]Assistant[/bold magenta]:")
        console.print(data["answer"])
        if data.get("sql"):
            console.print("\n[bold]SQL:[/bold]")
            console.print(data["sql"])
        console.print()


if __name__ == "__main__":
    main()
