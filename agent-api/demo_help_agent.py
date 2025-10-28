#!/usr/bin/env python3
"""
Quick demo script for Help/Onboarding Agent
Shows Priority 1 routing and help vs domain query distinction
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def demo_help_detection():
    """Demo the help query detection logic"""
    from agents.help_agent import HelpAgent

    console.print("\n[bold cyan]═══════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]     HELP AGENT DETECTION DEMO[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════[/bold cyan]\n")

    test_scenarios = [
        # Help queries (Priority 1)
        ("How do I use this system as a nurse?", True, "Help - onboarding", "🟢"),
        ("What questions can I ask?", True, "Help - guidance", "🟢"),
        ("Can I check pharmacy inventory here?", True, "Help - capability check", "🟢"),
        ("¿Cómo puedo usar este sistema?", True, "Help - Spanish", "🟢"),
        ("Comment utiliser ce système?", True, "Help - French", "🟢"),
        ("Wie benutze ich dieses System?", True, "Help - German", "🟢"),

        # Domain queries (Priority 2)
        ("How do I insert an IV line?", False, "Nursing - actual question", "🔵"),
        ("How many vacation days do I have?", False, "HR - actual question", "🔵"),
        ("Is ibuprofen 400mg in stock?", False, "Pharmacy - actual question", "🔵"),
        ("¿Cómo curar una herida?", False, "Nursing - Spanish", "🔵"),
    ]

    for query, expected_help, description, emoji in test_scenarios:
        is_help = HelpAgent.is_help_query(query)

        if is_help:
            route = "[green]Help Agent[/green]"
            priority = "[yellow]Priority 1[/yellow]"
        else:
            route = "[blue]Domain Agent[/blue]"
            priority = "[cyan]Priority 2[/cyan]"

        status = "✓" if is_help == expected_help else "✗"

        console.print(f"\n{status} {emoji} [bold]{description}[/bold]")
        console.print(f"   Query: [italic]\"{query}\"[/italic]")
        console.print(f"   Route: {route} | {priority}")

    console.print("\n[bold cyan]═══════════════════════════════════════════════════[/bold cyan]\n")


def demo_orchestrator_integration():
    """Demo the orchestrator with help agent"""
    console.print("\n[bold magenta]═══════════════════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]     ORCHESTRATOR INTEGRATION DEMO[/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════════════════[/bold magenta]\n")

    try:
        from orchestrator import HospitalOrchestrator

        console.print("[yellow]Initializing orchestrator...[/yellow]")
        orch = HospitalOrchestrator()

        console.print("[green]✓ Orchestrator initialized with 4 agents[/green]\n")

        # Get agent info
        info = orch.get_agent_info()
        console.print("[bold]Available Agents:[/bold]")
        for agent_name, agent_info in info['agents'].items():
            priority = agent_info.get('priority', 'N/A')
            console.print(f"  • {agent_name}: {agent_info['name']} (Priority {priority})")

        console.print("\n[bold cyan]Test Scenario 1: Help Query[/bold cyan]")
        console.print("Query: [italic]\"How do I use this system as a nurse?\"[/italic]\n")

        try:
            result = orch.process_query("How do I use this system as a nurse?")

            console.print(Panel(
                f"[green]✓ Routed to: {result['agent']}[/green]\n"
                f"Priority: {result['routing_info']['priority']}\n"
                f"Method: {result['routing_info']['method']}\n"
                f"Language: {result.get('language', 'N/A')}",
                title="Routing Result",
                border_style="green"
            ))

            # Show first 300 chars of answer
            answer_preview = result['answer'][:300] + "..." if len(result['answer']) > 300 else result['answer']
            console.print("\n[bold]Answer Preview:[/bold]")
            console.print(Panel(answer_preview, border_style="cyan"))

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            console.print("[yellow]Note: This requires valid GCP credentials and datastore setup[/yellow]")

        console.print("\n[bold cyan]Test Scenario 2: Domain Query[/bold cyan]")
        console.print("Query: [italic]\"How do I insert an IV?\"[/italic]\n")
        console.print("[yellow]This should route to Nursing Agent (Priority 2), NOT Help Agent[/yellow]\n")

        try:
            result = orch.process_query("How do I insert an IV?")

            console.print(Panel(
                f"[blue]✓ Routed to: {result['agent']}[/blue]\n"
                f"Priority: {result['routing_info']['priority']}\n"
                f"Method: {result['routing_info']['method']}",
                title="Routing Result",
                border_style="blue"
            ))

            if result['agent'] != 'help':
                console.print("[green]✓ Correct! Domain question routed to domain agent[/green]")
            else:
                console.print("[red]✗ Incorrect! Should not route to help agent[/red]")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            console.print("[yellow]Note: This requires valid GCP credentials and datastore setup[/yellow]")

    except ImportError as e:
        console.print(f"[red]Import Error: {str(e)}[/red]")
        console.print("[yellow]Some required packages may not be installed[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print("[yellow]Note: Full demo requires GCP credentials and datastore setup[/yellow]")

    console.print("\n[bold magenta]═══════════════════════════════════════════════════[/bold magenta]\n")


def show_example_scenarios():
    """Show example help queries in multiple languages"""
    console.print("\n[bold yellow]═══════════════════════════════════════════════════[/bold yellow]")
    console.print("[bold yellow]     EXAMPLE HELP QUERIES (4 LANGUAGES)[/bold yellow]")
    console.print("[bold yellow]═══════════════════════════════════════════════════[/bold yellow]\n")

    examples = {
        "English": [
            "How do I use this system as a nurse?",
            "What questions can I ask about HR?",
            "Can I check medication inventory here?",
            "What is this tool for?"
        ],
        "Spanish": [
            "¿Cómo puedo usar este sistema como enfermera?",
            "¿Qué preguntas puedo hacer?",
            "¿Puedo consultar el inventario de medicamentos aquí?"
        ],
        "French": [
            "Comment utiliser ce système?",
            "Quelles questions puis-je poser?",
            "Puis-je vérifier l'inventaire ici?"
        ],
        "German": [
            "Wie benutze ich dieses System?",
            "Welche Fragen kann ich stellen?",
            "Kann ich hier Medikamente prüfen?"
        ]
    }

    for language, queries in examples.items():
        console.print(f"[bold cyan]{language}:[/bold cyan]")
        for query in queries:
            console.print(f"  • \"{query}\"")
        console.print()

    console.print("[bold yellow]═══════════════════════════════════════════════════[/bold yellow]\n")


def main():
    """Run the demo"""
    console.print("\n[bold green]🎯 Hospital Multi-Agent System - Help Agent Demo[/bold green]\n")

    # Demo 1: Detection logic
    demo_help_detection()

    # Demo 2: Example queries
    show_example_scenarios()

    # Demo 3: Orchestrator integration (requires GCP setup)
    if "--full" in sys.argv or "-f" in sys.argv:
        demo_orchestrator_integration()
    else:
        console.print("[yellow]💡 Run with --full or -f flag to test orchestrator integration[/yellow]")
        console.print("[yellow]   (requires GCP credentials and datastore setup)[/yellow]\n")

    console.print("[bold green]✓ Demo complete![/bold green]\n")


if __name__ == "__main__":
    main()
