#!/usr/bin/env python3
"""
Quick test for Research Agent - Single query test
"""

import sys
from config import config
from agents.research_agent import ResearchAgent
from agents.nursing_agent import NursingAgent
from agents.pharmacy_agent import PharmacyAgent

def main():
    print("=" * 80)
    print("RESEARCH AGENT QUICK TEST")
    print("=" * 80)

    # Initialize agents
    print("\n[1/4] Initializing NursingAgent...")
    nursing = NursingAgent(project_id=config.PROJECT_ID, location=config.LOCATION)
    print("✓ NursingAgent ready")

    print("\n[2/4] Initializing PharmacyAgent...")
    pharmacy = PharmacyAgent(project_id=config.PROJECT_ID, location=config.LOCATION)
    print("✓ PharmacyAgent ready")

    print("\n[3/4] Initializing ResearchAgent...")
    research = ResearchAgent(
        project_id=config.PROJECT_ID,
        nursing_agent=nursing,
        pharmacy_agent=pharmacy,
        location=config.LOCATION,
        max_iterations=10
    )
    print("✓ ResearchAgent ready")

    # Test query
    print("\n[4/4] Testing research query...")
    print("-" * 80)
    query = "What do I need to do today with patient Juan de Marco?"
    print(f"Query: {query}")
    print("-" * 80)

    result = research.research(query)

    if result.get('error'):
        print(f"\n❌ ERROR: {result.get('message')}")
        return 1

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result['answer'])

    print("\n" + "=" * 80)
    print("METADATA")
    print("=" * 80)
    print(f"Iterations: {result['iterations']}")
    print(f"Tool Calls: {result['tool_calls']}")

    if result.get('tool_call_history'):
        print("\nTool Call Trace:")
        for i, call in enumerate(result['tool_call_history'], 1):
            print(f"  {i}. [{call['function']}] - {call['arguments']}")

    print("\n" + "=" * 80)
    print("✓ TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
