#!/usr/bin/env python3
"""
Test script for conversation context feature
Tests that follow-up questions work with conversation history
"""

from orchestrator import HospitalOrchestrator
from rich.console import Console

console = Console()


def test_conversation_context():
    """Test that conversation context enables follow-up questions"""

    console.print("\n[bold cyan]Testing Conversation Context[/bold cyan]")
    console.print("=" * 70)

    # Initialize orchestrator
    orchestrator = HospitalOrchestrator()

    # Test Case 1: HR - Vacation days follow-up
    console.print("\n[yellow]Test Case 1: HR - Vacation Days Follow-up[/yellow]")
    console.print("-" * 70)

    # First query - establish context
    query1 = "How many vacation days do I get?"
    console.print(f"\n[green]Query 1:[/green] {query1}")

    result1 = orchestrator.process_query(query1, user_role="employee")

    if not result1.get('error'):
        answer1 = result1['answer']
        console.print(f"[blue]Answer 1:[/blue] {answer1[:200]}...")

        # Build conversation history
        conversation_history = [
            {"role": "user", "content": query1},
            {"role": "assistant", "content": answer1}
        ]

        # Follow-up query - should understand "they" refers to vacation days
        query2 = "Can I carry them over to next year?"
        console.print(f"\n[green]Query 2 (Follow-up):[/green] {query2}")

        result2 = orchestrator.process_query(
            query2,
            user_role="employee",
            conversation_history=conversation_history
        )

        if not result2.get('error'):
            answer2 = result2['answer']
            console.print(f"[blue]Answer 2:[/blue] {answer2[:200]}...")
            console.print("\n[bold green]✓ Test Case 1 PASSED[/bold green]")
        else:
            console.print(f"\n[bold red]✗ Test Case 1 FAILED: {result2.get('message')}[/bold red]")
    else:
        console.print(f"\n[bold red]✗ Test Case 1 FAILED: {result1.get('message')}[/bold red]")

    # Test Case 2: Nursing - IV insertion follow-up
    console.print("\n\n[yellow]Test Case 2: Nursing - IV Insertion Follow-up[/yellow]")
    console.print("-" * 70)

    # First query
    query3 = "How do I insert an IV line?"
    console.print(f"\n[green]Query 3:[/green] {query3}")

    result3 = orchestrator.process_query(query3, user_role="nurse")

    if not result3.get('error'):
        answer3 = result3['answer']
        console.print(f"[blue]Answer 3:[/blue] {answer3[:200]}...")

        # Build conversation history
        conversation_history2 = [
            {"role": "user", "content": query3},
            {"role": "assistant", "content": answer3}
        ]

        # Follow-up query
        query4 = "What equipment do I need for that?"
        console.print(f"\n[green]Query 4 (Follow-up):[/green] {query4}")

        result4 = orchestrator.process_query(
            query4,
            user_role="nurse",
            conversation_history=conversation_history2
        )

        if not result4.get('error'):
            answer4 = result4['answer']
            console.print(f"[blue]Answer 4:[/blue] {answer4[:200]}...")
            console.print("\n[bold green]✓ Test Case 2 PASSED[/bold green]")
        else:
            console.print(f"\n[bold red]✗ Test Case 2 FAILED: {result4.get('message')}[/bold red]")
    else:
        console.print(f"\n[bold red]✗ Test Case 2 FAILED: {result3.get('message')}[/bold red]")

    # Test Case 3: No history - baseline
    console.print("\n\n[yellow]Test Case 3: Baseline (No History)[/yellow]")
    console.print("-" * 70)

    query5 = "What about blood glucose monitoring?"
    console.print(f"\n[green]Query 5:[/green] {query5}")

    result5 = orchestrator.process_query(query5, user_role="nurse")

    if not result5.get('error'):
        answer5 = result5['answer']
        console.print(f"[blue]Answer 5:[/blue] {answer5[:200]}...")
        console.print("\n[bold green]✓ Test Case 3 PASSED[/bold green]")
    else:
        console.print(f"\n[bold red]✗ Test Case 3 FAILED: {result5.get('message')}[/bold red]")

    console.print("\n" + "=" * 70)
    console.print("[bold cyan]Conversation Context Tests Complete![/bold cyan]\n")


if __name__ == "__main__":
    test_conversation_context()
