#!/usr/bin/env python3
"""Test ADK with queries using exact document terms."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adk_agent.hospital_agent_vertex import chat_with_agent

print("🏥 ADK Agent - Real World Test")
print("=" * 70)

test_queries = [
    "How do I insert a peripheral IV?",
    "What is the procedure for an indwelling urinary catheter?",
    "Tell me about central line dressing changes"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*70}")
    print(f"TEST {i}/{len(test_queries)}")
    print('=' * 70)
    print(f"👤 User: {query}\n")
    
    result = chat_with_agent(query)
    print(f"🤖 Agent:\n{result['answer']}\n")
    print(f"📚 Sources: {result['sources']}")
    
    if i < len(test_queries):
        print(f"\n⏳ Waiting 8 seconds to avoid rate limit...")
        time.sleep(8)

print("\n" + "=" * 70)
print("✅ Testing Complete!")
print("=" * 70)
