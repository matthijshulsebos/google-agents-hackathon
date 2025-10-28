#!/usr/bin/env python3
"""
Interactive Hospital Chat Assistant - Terminal Interface
Run this to chat with your hospital assistant in the terminal.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adk_agent.hospital_agent_vertex import chat_with_agent

def main():
    print("=" * 70)
    print("🏥 Hospital AI Assistant")
    print("=" * 70)
    print("\nI can help you with:")
    print("  • Nursing procedures and protocols")
    print("  • Pharmacy information and medications")
    print("  • HR policies and procedures")
    print("\nType 'quit' or 'exit' to end the conversation")
    print("=" * 70)
    
    chat_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thank you for using Hospital AI Assistant. Goodbye!")
                break
            
            # Get response from agent
            print("\n🤔 Thinking...")
            result = chat_with_agent(user_input, chat_history)
            
            # Display response
            print(f"\n🤖 Assistant:\n{result['answer']}")
            
            if result['sources']:
                print(f"\n📚 Sources: {', '.join(result['sources'])}")
            
            # Update chat history for context
            chat_history = result.get('chat_history', [])
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
