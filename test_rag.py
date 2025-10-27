#!/usr/bin/env python3
"""
Test script for the Hospital Multi-Agent RAG System
Run this to test the new Vertex AI Search integration
"""

from orchestrator import HospitalOrchestrator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_result(result, query):
    """Pretty print a query result"""

    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}")

    if result.get('error'):
        console.print(f"[red]❌ ERROR:[/red] {result['message']}")
        return

    # Create info table
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Agent", result.get('agent', 'unknown').upper())
    table.add_row("Language", result.get('language', 'unknown').upper())
    table.add_row("Total Results", str(result.get('total_results', 0)))
    table.add_row("Sources Used", str(len(result.get('grounding_metadata', []))))

    console.print(table)

    # Print answer
    answer = result.get('answer', 'No answer')
    panel = Panel(answer, title="[bold green]Answer[/bold green]", border_style="green")
    console.print(panel)


def test_nursing_queries():
    """Test nursing-related queries"""
    console.print("\n[bold yellow]Testing Nursing Agent[/bold yellow]")
    console.print("="*70)

    queries = [
        "What about blood glucose monitoring?",
        "How do I insert an IV line?",
        "What are the steps for wound dressing?",
        "Tell me about vital signs monitoring",
    ]

    orch = HospitalOrchestrator()

    for query in queries:
        result = orch.process_query(query)
        print_result(result, query)
        console.print()


def test_multilingual():
    """Test multilingual support"""
    console.print("\n[bold yellow]Testing Multilingual Support[/bold yellow]")
    console.print("="*70)

    queries = [
        ("en", "How do I insert an IV?"),
        ("es", "¿Cuál es el protocolo para curar heridas?"),
    ]

    orch = HospitalOrchestrator()

    for lang, query in queries:
        console.print(f"\n[dim]Language: {lang.upper()}[/dim]")
        result = orch.process_query(query)
        print_result(result, query)


def interactive_mode():
    """Interactive testing mode"""
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("Type your queries (or 'exit' to quit)")
    console.print("="*70)

    orch = HospitalOrchestrator()

    while True:
        try:
            query = console.input("\n[yellow]Your query:[/yellow] ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                console.print("[cyan]Goodbye![/cyan]")
                break

            result = orch.process_query(query)
            print_result(result, query)

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


def main():
    """Main test menu"""
    console.print("""
    [bold green]╔═══════════════════════════════════════════════════════════╗
    ║   Hospital Multi-Agent RAG System - Test Suite          ║
    ╚═══════════════════════════════════════════════════════════╝[/bold green]
    """)

    console.print("Select test mode:")
    console.print("1. Test Nursing Queries (automated)")
    console.print("2. Test Multilingual Support")
    console.print("3. Interactive Mode (ask your own questions)")
    console.print("4. Quick Single Test")
    console.print("0. Exit")

    choice = console.input("\n[yellow]Enter choice (0-4):[/yellow] ").strip()

    if choice == "1":
        test_nursing_queries()
    elif choice == "2":
        test_multilingual()
    elif choice == "3":
        interactive_mode()
    elif choice == "4":
        console.print("\n[bold]Quick Test: Blood Glucose Monitoring[/bold]")
        orch = HospitalOrchestrator()
        result = orch.process_query("What about blood glucose monitoring?")
        print_result(result, "What about blood glucose monitoring?")
    elif choice == "0":
        console.print("[cyan]Goodbye![/cyan]")
    else:
        console.print("[red]Invalid choice[/red]")


if __name__ == "__main__":
    main()
