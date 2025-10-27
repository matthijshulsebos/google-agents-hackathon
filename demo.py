"""
Demo script for Hospital Multi-Agent Information Retrieval System
Showcases multilingual capabilities and intelligent routing
"""
import json
from datetime import datetime
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from orchestrator import HospitalOrchestrator
from config import config

console = Console()


def print_banner():
    """Print demo banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║   Hospital Multi-Agent Information Retrieval System      ║
║   Powered by Google ADK & Vertex AI Search               ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_scenario_header(scenario_num: int, total: int, description: str):
    """Print scenario header"""
    console.print(f"\n{'='*60}", style="bold")
    console.print(f"Scenario {scenario_num}/{total}: {description}", style="bold yellow")
    console.print(f"{'='*60}", style="bold")


def print_query(query: str, language: str, user_role: str = None):
    """Print query information"""
    table = Table(show_header=False, box=None)
    table.add_column("Label", style="cyan", width=15)
    table.add_column("Value", style="white")

    table.add_row("Query:", query)
    table.add_row("Language:", language.upper())
    if user_role:
        table.add_row("User Role:", user_role.title())

    console.print(table)
    console.print()


def print_response(result: Dict[str, Any]):
    """Print agent response"""
    if result.get('error'):
        console.print(f"[red]Error: {result.get('message', 'Unknown error')}[/red]")
        return

    # Agent and routing info
    agent = result.get('agent', 'unknown')
    routing = result.get('routing_info', {})

    console.print(f"[green]✓ Routed to: {agent.upper()} Agent[/green]")
    console.print(f"  Method: {routing.get('method', 'unknown')}")
    console.print(f"  Confidence: {routing.get('confidence', 'unknown')}")
    console.print()

    # Answer
    answer = result.get('answer', 'No answer generated')
    panel = Panel(answer, title="Response", border_style="green")
    console.print(panel)

    # Citations
    grounding = result.get('grounding_metadata')
    if grounding and len(grounding) > 0:
        console.print(f"\n[dim]📚 Sources: {len(grounding)} documents cited[/dim]")


def run_demo_scenarios(orchestrator: HospitalOrchestrator, save_results: bool = True):
    """
    Run comprehensive demo scenarios

    Args:
        orchestrator: HospitalOrchestrator instance
        save_results: Whether to save results to JSON file
    """
    # Define demo scenarios
    scenarios = [
        # Nursing scenarios (English & Spanish)
        {
            "description": "Nursing - IV Insertion (English)",
            "query": "How do I insert an IV line?",
            "language": "en",
            "user_role": "nurse",
            "expected_agent": "nursing"
        },
        {
            "description": "Nursing - Wound Care (Spanish)",
            "query": "¿Cuál es el protocolo para curar heridas?",
            "language": "es",
            "user_role": "nurse",
            "expected_agent": "nursing"
        },
        {
            "description": "Nursing - Safety Protocol (English)",
            "query": "What are the safety considerations for IV insertion?",
            "language": "en",
            "user_role": "nurse",
            "expected_agent": "nursing"
        },

        # HR scenarios (English & French)
        {
            "description": "HR - Vacation Days (English)",
            "query": "How many vacation days do I get per year?",
            "language": "en",
            "user_role": "employee",
            "expected_agent": "hr"
        },
        {
            "description": "HR - Public Holidays (French)",
            "query": "Quels sont les jours fériés pour 2025?",
            "language": "fr",
            "user_role": "employee",
            "expected_agent": "hr"
        },
        {
            "description": "HR - Leave Request (English)",
            "query": "How do I request time off?",
            "language": "en",
            "user_role": "employee",
            "expected_agent": "hr"
        },

        # Pharmacy scenarios (English & German)
        {
            "description": "Pharmacy - Medication Check (English)",
            "query": "Is ibuprofen 400mg in stock?",
            "language": "en",
            "user_role": "pharmacist",
            "expected_agent": "pharmacy"
        },
        {
            "description": "Pharmacy - Availability (German)",
            "query": "Ist Paracetamol auf Lager?",
            "language": "de",
            "user_role": "pharmacist",
            "expected_agent": "pharmacy"
        },
        {
            "description": "Pharmacy - Antibiotic Inventory (English)",
            "query": "Which antibiotics are available?",
            "language": "en",
            "user_role": "pharmacist",
            "expected_agent": "pharmacy"
        },

        # Intelligent routing (no role specified)
        {
            "description": "Auto-Routing - Medical Query",
            "query": "What equipment do I need for wound dressing?",
            "language": "en",
            "user_role": None,
            "expected_agent": "nursing"
        },
        {
            "description": "Auto-Routing - HR Query",
            "query": "Can I carry over vacation days?",
            "language": "en",
            "user_role": None,
            "expected_agent": "hr"
        },
        {
            "description": "Auto-Routing - Pharmacy Query",
            "query": "Do we have insulin in the pharmacy?",
            "language": "en",
            "user_role": None,
            "expected_agent": "pharmacy"
        },
    ]

    results = []
    total_scenarios = len(scenarios)

    for idx, scenario in enumerate(scenarios, 1):
        print_scenario_header(idx, total_scenarios, scenario['description'])

        print_query(
            query=scenario['query'],
            language=scenario['language'],
            user_role=scenario.get('user_role')
        )

        # Process query
        with console.status(f"[bold cyan]Processing query..."):
            result = orchestrator.process_query(
                query=scenario['query'],
                user_role=scenario.get('user_role')
            )

        # Print response
        print_response(result)

        # Verify routing
        actual_agent = result.get('agent')
        expected_agent = scenario.get('expected_agent')

        if actual_agent == expected_agent:
            console.print(f"[green]✓ Routing correct: {expected_agent}[/green]\n")
        else:
            console.print(
                f"[yellow]⚠ Routing mismatch: expected {expected_agent}, "
                f"got {actual_agent}[/yellow]\n"
            )

        # Save result
        results.append({
            "scenario": scenario['description'],
            "query": scenario['query'],
            "language": scenario['language'],
            "user_role": scenario.get('user_role'),
            "expected_agent": expected_agent,
            "actual_agent": actual_agent,
            "routing_correct": actual_agent == expected_agent,
            "result": result
        })

        # Small delay for readability
        import time
        time.sleep(0.5)

    # Save results if requested
    if save_results:
        output_file = f"outputs/demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        console.print(f"\n[cyan]Results saved to: {output_file}[/cyan]")

    # Print summary
    print_summary(results)

    return results


def print_summary(results: List[Dict[str, Any]]):
    """Print demo summary statistics"""
    console.print("\n" + "="*60, style="bold")
    console.print("DEMO SUMMARY", style="bold yellow")
    console.print("="*60, style="bold")

    total = len(results)
    correct_routing = sum(1 for r in results if r['routing_correct'])
    accuracy = (correct_routing / total * 100) if total > 0 else 0

    # Create summary table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white", justify="right")

    table.add_row("Total Scenarios", str(total))
    table.add_row("Correct Routing", str(correct_routing))
    table.add_row("Routing Accuracy", f"{accuracy:.1f}%")

    # Count by agent
    agent_counts = {}
    for r in results:
        agent = r['actual_agent']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1

    table.add_row("", "")  # Separator
    for agent, count in agent_counts.items():
        table.add_row(f"{agent.title()} Agent", str(count))

    # Count by language
    lang_counts = {}
    for r in results:
        lang = r['language']
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    table.add_row("", "")  # Separator
    for lang, count in lang_counts.items():
        table.add_row(f"{lang.upper()} Queries", str(count))

    console.print(table)

    # Success message
    if accuracy >= 90:
        console.print("\n[bold green]✓ Demo completed successfully![/bold green]")
    elif accuracy >= 75:
        console.print("\n[bold yellow]⚠ Demo completed with some routing issues[/bold yellow]")
    else:
        console.print("\n[bold red]✗ Demo completed with significant routing issues[/bold red]")


def interactive_mode(orchestrator: HospitalOrchestrator):
    """
    Interactive mode for live queries

    Args:
        orchestrator: HospitalOrchestrator instance
    """
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("Enter your queries (type 'exit' to quit, 'info' for agent info)\n")

    while True:
        try:
            query = console.input("[bold yellow]Query:[/bold yellow] ").strip()

            if not query:
                continue

            if query.lower() == 'exit':
                console.print("[cyan]Exiting interactive mode...[/cyan]")
                break

            if query.lower() == 'info':
                info = orchestrator.get_agent_info()
                console.print(json.dumps(info, indent=2))
                continue

            # Process query
            with console.status("[bold cyan]Processing..."):
                result = orchestrator.process_query(query)

            console.print()
            print_response(result)
            console.print()

        except KeyboardInterrupt:
            console.print("\n[cyan]Exiting interactive mode...[/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


def main():
    """Main demo function"""
    print_banner()

    try:
        # Display configuration
        console.print("[cyan]Configuration:[/cyan]")
        config.display_config()

        # Initialize orchestrator
        console.print("\n[bold cyan]Initializing Hospital Orchestrator...[/bold cyan]")

        try:
            orchestrator = HospitalOrchestrator()
            console.print("[green]✓ Orchestrator initialized successfully[/green]\n")
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize orchestrator: {str(e)}[/red]")
            console.print("\n[yellow]Note: Make sure to configure your .env file with valid GCP credentials[/yellow]")
            return

        # Health check
        console.print("[cyan]Performing health check...[/cyan]")
        health = orchestrator.health_check()

        if health['orchestrator'] == 'healthy':
            console.print("[green]✓ All systems healthy[/green]\n")
        else:
            console.print("[yellow]⚠ Some systems may be unavailable[/yellow]")
            console.print(json.dumps(health, indent=2))
            console.print()

        # Run demo scenarios
        console.print("[bold cyan]Starting Demo Scenarios...[/bold cyan]\n")
        results = run_demo_scenarios(orchestrator, save_results=True)

        # Optional: Interactive mode
        console.print("\n[cyan]Would you like to enter interactive mode? (y/n)[/cyan]")
        choice = input().strip().lower()

        if choice == 'y':
            interactive_mode(orchestrator)

        console.print("\n[bold cyan]Demo completed! Thank you for watching.[/bold cyan]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
