"""
Hospital ADK Agent - Using Modern Google GenAI SDK
Production-ready agent using Google's latest GenAI SDK (not deprecated)
"""
from google import genai
from google.genai import types
import os
import sys
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import settings which already loads .env
from src.config import settings

# Initialize
PROJECT_ID = settings.gcp_project_id
DATASTORE_LOCATION = settings.gcp_location  # "eu" for datastores
GEMINI_LOCATION = "us-central1"  # Gemini API location

print(f"🔧 Config: Project={PROJECT_ID}")
print(f"   Datastores: {DATASTORE_LOCATION}, Gemini: {GEMINI_LOCATION}")

# Initialize GenAI client (modern, not deprecated)
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=GEMINI_LOCATION
)


# Define search tool functions
def search_nursing_domain(query: str) -> Dict[str, Any]:
    """Search the nursing domain for relevant policies and procedures."""
    from src.agents.domain_agents import AgentRegistry
    from src.config import config, settings
    
    print(f"  → Searching nursing datastore for: '{query}'")
    
    registry = AgentRegistry(
        project_id=settings.gcp_project_id,
        location=settings.gcp_location,
        config=config
    )
    
    nursing_agent = registry.get_agent("nursing")
    if not nursing_agent:
        return {"error": "Nursing agent not available"}
    
    results = nursing_agent.search(query)
    print(f"  → Found {len(results)} raw results")
    
    formatted_results = []
    for r in results[:3]:
        formatted_results.append({
            "text": r.get("content", ""),  # Full content
            "source": r.get("metadata", {}).get("filename", "")
        })
    
    return {
        "domain": "nursing",
        "results": formatted_results,
        "count": len(results)
    }


def search_pharmacy_domain(query: str) -> Dict[str, Any]:
    """Search the pharmacy domain for medication information and guidelines."""
    from src.agents.domain_agents import AgentRegistry
    from src.config import config, settings
    
    registry = AgentRegistry(
        project_id=settings.gcp_project_id,
        location=settings.gcp_location,
        config=config
    )
    
    pharmacy_agent = registry.get_agent("pharmacy")
    if not pharmacy_agent:
        return {"error": "Pharmacy agent not available"}
    
    results = pharmacy_agent.search(query)
    return {
        "domain": "pharmacy",
        "results": [{"text": r.get("content", ""), "source": r.get("metadata", {}).get("filename", "")} for r in results[:3]],
        "count": len(results)
    }


def search_hr_domain(query: str) -> Dict[str, Any]:
    """Search the HR domain for employee policies and procedures."""
    from src.agents.domain_agents import AgentRegistry
    from src.config import config, settings
    
    registry = AgentRegistry(
        project_id=settings.gcp_project_id,
        location=settings.gcp_location,
        config=config
    )
    
    hr_agent = registry.get_agent("po")
    if not hr_agent:
        return {"error": "HR agent not available"}
    
    results = hr_agent.search(query)
    return {
        "domain": "hr",
        "results": [{"text": r.get("content", ""), "source": r.get("metadata", {}).get("filename", "")} for r in results[:3]],
        "count": len(results)
    }


# Define tools for the model using modern GenAI SDK
search_nursing_tool = types.FunctionDeclaration(
    name="search_nursing_domain",
    description="Search nursing policies, procedures, and clinical guidelines",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query for nursing information"
            }
        },
        "required": ["query"]
    }
)

search_pharmacy_tool = types.FunctionDeclaration(
    name="search_pharmacy_domain",
    description="Search pharmacy information, medication guidelines, and drug procedures",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query for pharmacy information"
            }
        },
        "required": ["query"]
    }
)

search_hr_tool = types.FunctionDeclaration(
    name="search_hr_domain",
    description="Search HR policies, employee benefits, and personnel procedures",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query for HR information"
            }
        },
        "required": ["query"]
    }
)

# Create tool
hospital_tool = types.Tool(
    function_declarations=[
        search_nursing_tool,
        search_pharmacy_tool,
        search_hr_tool
    ]
)

# System instruction
SYSTEM_INSTRUCTION = """You are a helpful Hospital AI Assistant with access to three specialized knowledge domains:

1. **Nursing**: Patient care procedures, nursing protocols, clinical guidelines
2. **Pharmacy**: Medication information, drug interactions, pharmacy procedures
3. **HR**: Employee policies, benefits, hiring procedures, training requirements

Your capabilities:
- You can search any of these domains using the provided tools
- Always cite your sources when providing information
- If a question spans multiple domains, search all relevant domains
- Be precise and professional in your responses

Remember:
- Always ground your answers in the search results
- Cite specific document sources
- If information is not in the search results, say so
"""


def chat_with_agent(user_message: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Chat with the hospital agent using modern GenAI SDK
    
    Args:
        user_message: The user's question
        chat_history: Previous conversation history
        
    Returns:
        Dictionary with agent response and sources
    """
    if chat_history is None:
        chat_history = []
    
    try:
        # Map function names to actual functions
        function_map = {
            "search_nursing_domain": search_nursing_domain,
            "search_pharmacy_domain": search_pharmacy_domain,
            "search_hr_domain": search_hr_domain
        }
        
        # Build messages
        messages = chat_history + [
            types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        ]
        
        # Generate response with function calling (modern SDK)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[hospital_tool],
                temperature=0.2
            )
        )
        
        sources = []
        
        # Handle function calls
        while response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = dict(function_call.args)
            
            print(f"🔍 Agent calling: {function_name}({function_args})")
            
            # Execute function
            function_result = function_map[function_name](**function_args)
            
            # Collect sources
            if "results" in function_result:
                for result in function_result["results"]:
                    if "source" in result and result["source"]:
                        sources.append(result["source"])
            
            # Add function call to messages
            messages.append(types.Content(
                role="model",
                parts=[types.Part(function_call=function_call)]
            ))
            
            # Add function response to messages
            messages.append(types.Content(
                role="user",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name=function_name,
                        response=function_result
                    )
                )]
            ))
            
            # Get next response
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[hospital_tool],
                    temperature=0.2
                )
            )
        
        # Get final text response
        answer = response.candidates[0].content.parts[0].text
        
        return {
            "answer": answer,
            "sources": list(set(sources)),  # Remove duplicates
            "chat_history": messages  # Return messages for conversation continuity
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "chat_history": []
        }


if __name__ == "__main__":
    print("🏥 Hospital ADK Agent Test (Modern GenAI SDK)")
    print("=" * 60)
    print()
    
    test_queries = [
        "What nursing information do you have?",
        "What medications are in stock in the pharmacy?",
        "What HR information is available?"
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        result = chat_with_agent(query)
        print(f"🤖 Agent: {result['answer']}")
        print(f"📚 Sources: {len(result['sources'])} document(s)")
        print()
