#!/usr/bin/env python3
"""
Research Agent Demo
Demonstrates agentic reasoning with tool calling for complex multi-step queries
"""

import sys
import logging
from datetime import datetime
from config import config
from agents.research_agent import ResearchAgent
from agents.nursing_agent import NursingAgent
from agents.pharmacy_agent import PharmacyAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title="", char="=", length=80):
    """Print a formatted separator"""
    if title:
        padding = (length - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(f"\n{char * length}")


def print_tool_calls(tool_call_history):
    """Print tool call history in a readable format"""
    print_separator("TOOL CALL TRACE", "-")

    for i, call in enumerate(tool_call_history, 1):
        print(f"\n[Iteration {call['iteration']}] Tool Call #{i}")
        print(f"  Function: {call['function']}")
        print(f"  Arguments: {call['arguments']}")
        print(f"  Result Preview: {call['result_summary'][:150]}...")


def run_research_demo():
    """Run research agent demo scenarios"""

    print_separator("HOSPITAL RESEARCH AGENT DEMO")
    print(f"Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
    print(f"Model: {config.MODEL_NAME}")
    print(f"Project: {config.PROJECT_ID}")

    # Validate configuration
    try:
        config.validate()
        print("✓ Configuration validated")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return

    # Initialize agents
    print_separator("INITIALIZING AGENTS", "-")

    try:
        # Initialize specialized agents
        print("Initializing NursingAgent...")
        nursing_agent = NursingAgent(
            project_id=config.PROJECT_ID,
            location=config.LOCATION
        )
        print("✓ NursingAgent ready")

        print("Initializing PharmacyAgent...")
        pharmacy_agent = PharmacyAgent(
            project_id=config.PROJECT_ID,
            location=config.LOCATION
        )
        print("✓ PharmacyAgent ready")

        # Initialize research agent
        print("Initializing ResearchAgent...")
        research_agent = ResearchAgent(
            project_id=config.PROJECT_ID,
            nursing_agent=nursing_agent,
            pharmacy_agent=pharmacy_agent,
            location=config.LOCATION,
            max_iterations=10
        )
        print("✓ ResearchAgent ready with agentic reasoning")

    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        return

    # Demo scenarios
    scenarios = [
        {
            "title": "Patient Care Research - Juan de Marco (Age 65, Scheduled Oxycodone)",
            "query": "What do I need to do today with patient Juan de Marco?",
            "description": """
This scenario demonstrates the agent's ability to:
1. Retrieve patient details (age: 65, scheduled for oxycodone)
2. Search nursing protocols for controlled medication administration
3. Check pharmacy audit dates for oxycodone
4. Reason about age-based requirements (>60 years = 6-month audit)
5. Identify compliance issues (audit overdue since April 2024)
6. Provide actionable recommendations
            """.strip()
        },
        {
            "title": "Patient Care Research - Maria Silva (Age 45, Standard Medication)",
            "query": "What medications is Maria Silva scheduled to receive today?",
            "description": """
This scenario shows simpler patient care queries where the agent:
1. Retrieves patient details (age: 45, scheduled for ibuprofen and omeprazole)
2. Provides straightforward medication schedule
3. No special protocols needed (under 60 years, non-controlled substances)
            """.strip()
        },
        {
            "title": "Protocol Research - Controlled Medication for Elderly",
            "query": "What are the special requirements for administering oxycodone to a 72-year-old patient?",
            "description": """
This scenario demonstrates protocol-focused research:
1. Search nursing protocols for age-specific requirements
2. Search pharmacy information for medication details
3. Synthesize requirements: dosing, monitoring, audit compliance
4. Provide comprehensive guidance
            """.strip()
        },
        {
            "title": "Inventory Check - Medication Availability",
            "query": "Is oxycodone 5mg available and can it be given to elderly patients today?",
            "description": """
This scenario combines inventory and compliance checks:
1. Search pharmacy inventory for oxycodone availability (580 tablets)
2. Check audit compliance for geriatric patients (overdue)
3. Provide inventory status with compliance warnings
            """.strip()
        }
    ]

    # Run scenarios
    for i, scenario in enumerate(scenarios, 1):
        print_separator(f"SCENARIO {i}/{len(scenarios)}: {scenario['title']}")

        print(f"\nDescription:")
        print(scenario['description'])

        print(f"\nQuery: \"{scenario['query']}\"")

        # Ask user if they want to continue
        user_input = input("\nPress Enter to run this scenario (or 'n' to skip): ").strip().lower()
        if user_input == 'n':
            print("Skipped.")
            continue

        print_separator("PROCESSING", "-")

        try:
            # Perform research
            start_time = datetime.now()
            result = research_agent.research(query=scenario['query'])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Check for errors
            if result.get('error'):
                print(f"\n❌ ERROR: {result.get('message', 'Unknown error')}")
                continue

            # Print results
            print_separator("RESEARCH RESULTS", "-")
            print(f"\nAnswer:\n{result['answer']}")

            # Print metadata
            print_separator("METADATA", "-")
            print(f"Agent: {result['agent']}")
            print(f"Iterations: {result['iterations']}")
            print(f"Tool Calls: {result['tool_calls']}")
            print(f"Processing Time: {duration:.2f} seconds")

            # Print tool call history
            if result.get('tool_call_history'):
                print_tool_calls(result['tool_call_history'])

            # Print warnings
            if result.get('warning'):
                print(f"\n⚠️  Warning: {result['warning']}")

        except Exception as e:
            logger.error(f"Error in scenario {i}: {e}")
            print(f"\n❌ Error: {e}")
            continue

        print_separator()

        # Add spacing between scenarios
        if i < len(scenarios):
            input("\nPress Enter to continue to next scenario...")

    # Summary
    print_separator("DEMO COMPLETED")
    print("""
Research Agent Capabilities Demonstrated:

✓ Multi-step reasoning with tool calling
✓ Patient data retrieval and analysis
✓ Nursing protocol compliance checking
✓ Pharmacy inventory and audit verification
✓ Age-specific requirement identification
✓ Cross-referencing multiple data sources
✓ Actionable recommendation generation
✓ ReAct-style agentic loop (Reason → Act → Observe)

Key Features:
- Gemini 2.5 Flash with function calling
- Up to 10 iterations for complex queries
- 3 specialized tools (patient data, nursing, pharmacy)
- Automatic reasoning trace capture
- Compliance and safety checking
    """)


def main():
    """Main entry point"""
    try:
        run_research_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
