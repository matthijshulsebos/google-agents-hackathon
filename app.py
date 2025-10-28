"""
Hospital AI Assistant - Streamlit Web Interface
Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.adk_agent.hospital_agent_vertex import chat_with_agent

# Page configuration
st.set_page_config(
    page_title="Hospital AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("🏥 Hospital AI Assistant")
st.markdown("Ask me anything about nursing procedures, pharmacy information, or HR policies!")

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.info("""
    This AI assistant can help you with:
    
    **Nursing Domain**
    - Clinical procedures
    - Patient care protocols
    - Medical guidelines
    
    **Pharmacy Domain**
    - Medication information
    - Drug inventory
    - Pharmacy procedures
    
    **HR Domain**
    - Employee policies
    - Benefits information
    - Personnel procedures
    """)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption(f"📚 Sources: {', '.join(message['sources'])}")

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = chat_with_agent(prompt, st.session_state.chat_history)
                
                # Display response
                st.markdown(result["answer"])
                
                # Display sources if available
                if result.get("sources"):
                    st.caption(f"📚 Sources: {', '.join(result['sources'])}")
                
                # Update chat history
                st.session_state.chat_history = result.get("chat_history", [])
                
                # Add assistant message to display
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", [])
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": []
                })

# Footer
st.markdown("---")
st.caption("Powered by Google Vertex AI Search & Gemini 2.0 Flash")
