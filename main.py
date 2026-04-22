"""Main entry point for AI Tax Buddy CLI."""

import logging
import typer
from rich.console import Console
from aitaxbuddy.agent import create_agent
from aitaxbuddy.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = typer.Typer()
console = Console()


@app.command()
def chat(
    user_id: str = typer.Option("default", help="User ID for memory persistence"),
):
    """Start an interactive chat session with AI Tax Buddy."""
    agent = create_agent(user_id=user_id)
    agent.chat()


@app.command()
def query(
    question: str = typer.Argument(..., help="The tax question to ask"),
    user_id: str = typer.Option("default", help="User ID for memory persistence"),
):
    """Ask a single question to AI Tax Buddy."""
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich import box
    
    agent = create_agent(user_id=user_id)
    
    # Show question
    console.print()
    console.print(Panel(
        f"[bold green]{question}[/bold green]",
        title="[bold]Your Question[/bold]",
        border_style="green",
        box=box.ROUNDED
    ))
    
    # Show thinking indicator
    with console.status("[bold cyan]Tax Buddy is thinking...[/bold cyan]", spinner="dots"):
        response = agent.process_message(question)
    
    # Show response
    console.print()
    console.print(Panel(
        Markdown(response),
        title="[bold cyan]💼 Tax Buddy[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    console.print()


@app.command()
def evaluate():
    """Run evaluation tests against the golden dataset."""
    from tests.evaluate_agent import run_evaluation
    
    console.print("\n[bold]Running AI Tax Buddy Evaluation...[/bold]\n")
    summary = run_evaluation()
    
    if summary["pass_rate"] >= 80:
        console.print("[bold green]✅ All tests passed![/bold green]")
    else:
        console.print("[bold red]⚠️  Some tests failed. Review the results above.[/bold red]")


@app.command()
def info():
    """Display configuration and system information."""
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    
    # Create configuration table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Model Provider", settings.model_provider)
    table.add_row("Model", settings.model_name)
    table.add_row("Temperature", str(settings.temperature))
    table.add_row("Environment", settings.environment)
    table.add_row("Max Iterations", str(settings.max_iterations))
    
    # Security features
    pii_status = "✅ Enabled" if settings.enable_pii_filtering else "❌ Disabled"
    guardrails_status = "✅ Enabled" if settings.enable_content_guardrails else "❌ Disabled"
    langfuse_status = "✅ Configured" if settings.langfuse_public_key else "⚠️  Not configured"
    
    table.add_row("", "")
    table.add_row("PII Filtering", pii_status)
    table.add_row("Content Guardrails", guardrails_status)
    table.add_row("Langfuse", langfuse_status)
    
    # Display in panel
    console.print()
    console.print(Panel(
        table,
        title="[bold cyan]🇦🇺 AI Tax Buddy Configuration[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2)
    ))
    console.print()


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
