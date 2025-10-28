"""
Hospital AI Assistant - Flask REST API
Run with: python api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.adk_agent.hospital_agent_vertex import chat_with_agent

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Store chat sessions (in production, use Redis or database)
chat_sessions = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Hospital AI Assistant"})

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint
    
    Request body:
    {
        "message": "What is the procedure for IV insertion?",
        "session_id": "optional-session-id"
    }
    """
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get or create chat history for this session
        chat_history = chat_sessions.get(session_id, [])
        
        # Get response from agent
        result = chat_with_agent(message, chat_history)
        
        # Update session history
        chat_sessions[session_id] = result.get('chat_history', [])
        
        return jsonify({
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear a chat session"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return jsonify({"message": "Session cleared", "session_id": session_id})

@app.route('/api/domains', methods=['GET'])
def get_domains():
    """Get available knowledge domains"""
    return jsonify({
        "domains": [
            {
                "name": "Nursing",
                "description": "Clinical procedures, patient care protocols, medical guidelines"
            },
            {
                "name": "Pharmacy",
                "description": "Medication information, drug inventory, pharmacy procedures"
            },
            {
                "name": "HR",
                "description": "Employee policies, benefits information, personnel procedures"
            }
        ]
    })

if __name__ == '__main__':
    print("🏥 Hospital AI Assistant API")
    print("=" * 70)
    print("Starting server on http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /api/chat - Send a message")
    print("  POST /api/clear-session - Clear chat history")
    print("  GET  /api/domains - Get available domains")
    print("  GET  /health - Health check")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
