"""
ADK-based Hospital Agent
Uses Google's Agent Development Kit to create a multi-domain search agent
"""
from google.cloud import aiplatform
from google import genai
from google.genai import types
import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import settings which already loads .env
from src.config import settings

# Initialize Vertex AI
PROJECT_ID = settings.gcp_project_id
DATASTORE_LOCATION = settings.gcp_location  # "eu" for datastores

# Gemini is most reliably available in us-central1
# Datastores can be in different region than Gemini API
GEMINI_LOCATION = "us-central1"  # Most reliable region for Gemini

print(f"🔧 Config: Datastores in '{DATASTORE_LOCATION}', Gemini API in '{GEMINI_LOCATION}'")

aiplatform.init(project=PROJECT_ID, location=GEMINI_LOCATION)

# Initialize Genai client for ADK
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=GEMINI_LOCATION  # Use Gemini-specific location
)


# Define tools for the agent
def search_nursing_domain(query: str) -> Dict[str, Any]:
    """
    Search the nursing domain for relevant policies and procedures.
    
    Args:
        query: The search query related to nursing
        
    Returns:
        Dictionary with search results and sources
    """
    from src.agents.domain_agents import AgentRegistry
    from src.config import config, settings
    
    # Initialize registry
    registry = AgentRegistry(
        project_id=settings.gcp_project_id,
        location=settings.gcp_location,
        config=config
    )
    
    # Get nursing agent
    nursing_agent = registry.get_agent("nursing")
    if not nursing_agent:
        return {"error": "Nursing agent not available"}
    
    # Search
    results = nursing_agent.search(query)
    return {
        "domain": "nursing",
        "results": results,
        "count": len(results)
    }


def search_pharmacy_domain(query: str) -> Dict[str, Any]:
    """
    Search the pharmacy domain for medication information and guidelines.
    
    Args:
        query: The search query related to pharmacy
        
    Returns:
        Dictionary with search results and sources
    """
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
        "results": results,
        "count": len(results)
    }


def search_hr_domain(query: str) -> Dict[str, Any]:
    """
    Search the HR domain for employee policies and procedures.
    
    Args:
        query: The search query related to HR
        
    Returns:
        Dictionary with search results and sources
    """
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
        "results": results,
        "count": len(results)
    }


# Define the agent's system instruction
SYSTEM_INSTRUCTION = """
You are a helpful Hospital AI Assistant with access to three specialized knowledge domains:

1. **Nursing**: Patient care procedures, nursing protocols, clinical guidelines
2. **Pharmacy**: Medication information, drug interactions, pharmacy procedures
3. **HR**: Employee policies, benefits, hiring procedures, training requirements

Your capabilities:
- You can search any of these domains using the provided tools
- Always cite your sources when providing information
- If a question spans multiple domains, search all relevant domains
- Be precise and professional in your responses
- If you're not sure which domain to search, search multiple domains

Remember:
- Always ground your answers in the search results
- Cite specific document sources
- If information is not in the search results, say so
- Be helpful but acknowledge limitations
"""


# Create the agent configuration
def create_hospital_agent():
    """Create and return the ADK agent with tools"""
    
    # Define tools for the agent
    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
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
                ),
                types.FunctionDeclaration(
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
                ),
                types.FunctionDeclaration(
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
            ]
        )
    ]
    
    # Map function names to actual functions
    function_map = {
        "search_nursing_domain": search_nursing_domain,
        "search_pharmacy_domain": search_pharmacy_domain,
        "search_hr_domain": search_hr_domain
    }
    
    return tools, function_map


def chat_with_agent(user_message: str, chat_history: list = None) -> Dict[str, Any]:
    """
    Chat with the ADK agent
    
    Args:
        user_message: The user's question
        chat_history: Previous conversation history
        
    Returns:
        Dictionary with agent response and sources
    """
    if chat_history is None:
        chat_history = []
    
    tools, function_map = create_hospital_agent()
    
    # Create chat session - using Gemini 2.0
    model = "gemini-2.0-flash-exp"
    
    # Build messages
    messages = chat_history + [
        types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        )
    ]
    
    # Generate response with function calling
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            temperature=0.2
        )
    )
    
    # Handle function calls
    sources = []
    while response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        # Execute the function
        function_response = function_map[function_name](**function_args)
        
        # Track sources
        if "results" in function_response:
            for result in function_response["results"]:
                if "metadata" in result:
                    sources.append(result["metadata"])
        
        # Add function response to messages
        messages.append(types.Content(
            role="model",
            parts=[types.Part(function_call=function_call)]
        ))
        
        messages.append(types.Content(
            role="user",
            parts=[types.Part(
                function_response=types.FunctionResponse(
                    name=function_name,
                    response=function_response
                )
            )]
        ))
        
        # Get next response
        response = client.models.generate_content(
            model=model,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=tools,
                temperature=0.2
            )
        )
    
    # Extract final answer
    answer = response.candidates[0].content.parts[0].text
    
    return {
        "answer": answer,
        "sources": sources,
        "chat_history": messages
    }


if __name__ == "__main__":
    # Test the agent
    print("🏥 Hospital ADK Agent Test\n")
    
    test_queries = [
        "What are the nursing protocols for patient intake?",
        "Tell me about medication dispensing procedures",
        "What are the employee benefits policies?"
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        result = chat_with_agent(query)
        print(f"🤖 Agent: {result['answer']}")
        print(f"📚 Sources: {len(result['sources'])} documents")
