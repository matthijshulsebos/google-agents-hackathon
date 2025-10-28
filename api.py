#!/usr/bin/env python3
"""
FastAPI HTTP API for Hospital Multi-Agent RAG System
Uses the current orchestrator.py and RAG pipeline
"""
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from orchestrator import HospitalOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Multi-Agent RAG System",
    description="AI-powered hospital information retrieval across Nursing, HR, and Pharmacy domains",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
orchestrator: Optional[HospitalOrchestrator] = None
research_agent = None  # Research agent instance
conversation_history: Dict[str, list] = {}  # Simple in-memory conversation storage


# Request/Response models
class QueryRequest(BaseModel):
    """Query request model."""
    query: str = Field(..., description="User's question", min_length=1)
    user_role: Optional[str] = Field(None, description="User role: nurse, employee, or pharmacist")
    agent_override: Optional[str] = Field(None, description="Force specific agent: nursing, hr, or pharmacy")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn")


class QueryResponse(BaseModel):
    """Query response model."""
    conversation_id: str = Field(..., description="Conversation ID")
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer (full detailed version)")
    answer_summary: str = Field(..., description="Concise 2-3 sentence summary")
    answer_detailed: str = Field(..., description="Full detailed answer with all information")
    agent: str = Field(..., description="Agent that handled the query")
    language: str = Field(..., description="Detected language")
    total_results: int = Field(..., description="Number of search results found")
    sources_count: int = Field(..., description="Number of sources cited")
    grounding_metadata: list = Field(..., description="Source citations")
    routing_info: Dict[str, Any] = Field(..., description="Routing decision information")
    timestamp: str = Field(..., description="Response timestamp")


class MultiAgentRequest(BaseModel):
    """Multi-agent query request model."""
    query: str = Field(..., description="User's question", min_length=1)
    agents: Optional[list] = Field(None, description="List of agents to query (default: all)")


class MultiAgentResponse(BaseModel):
    """Multi-agent query response model."""
    query: str
    timestamp: str
    results: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str
    orchestrator: str
    agents: Dict[str, Any]


class AgentInfoResponse(BaseModel):
    """Agent information response."""
    available_agents: list
    project_id: str
    location: str
    agents: Dict[str, Any]


class ResearchRequest(BaseModel):
    """Research request model."""
    query: str = Field(..., description="Research query", min_length=1)


class ResearchResponse(BaseModel):
    """Research response model."""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Full detailed research answer")
    answer_summary: str = Field(..., description="Concise 2-3 sentence summary for chatbot display")
    answer_detailed: str = Field(..., description="Full detailed answer with all information")
    agent: str = Field(..., description="Agent type (research)")
    iterations: int = Field(..., description="Number of reasoning iterations")
    tool_calls: int = Field(..., description="Number of tool calls made")
    tool_call_history: List[Dict[str, Any]] = Field(..., description="History of tool calls")
    timestamp: str = Field(..., description="Response timestamp")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global orchestrator, research_agent

    logger.info("Starting Hospital Multi-Agent RAG System...")

    try:
        # Initialize orchestrator
        logger.info("Initializing HospitalOrchestrator...")
        orchestrator = HospitalOrchestrator()

        # Initialize research agent
        logger.info("Initializing ResearchAgent...")
        from agents.research_agent import ResearchAgent
        from config import config
        research_agent = ResearchAgent(
            project_id=config.PROJECT_ID,
            nursing_agent=orchestrator.nursing_agent,
            hr_agent=orchestrator.hr_agent,
            pharmacy_agent=orchestrator.pharmacy_agent,
            location=config.LOCATION
        )

        logger.info("Hospital Multi-Agent RAG System started successfully!")

        # Run health check
        health = orchestrator.health_check()
        logger.info(f"Orchestrator status: {health['orchestrator']}")
        for agent_name, agent_status in health['agents'].items():
            if agent_status.get('healthy'):
                logger.info(f"  ✓ {agent_name} agent: {agent_status.get('implementation', 'ready')}")
            else:
                logger.warning(f"  ✗ {agent_name} agent: {agent_status.get('error', 'not healthy')}")

        logger.info("  ✓ research agent: initialized with tool-based reasoning")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Hospital Multi-Agent RAG System",
        "version": "2.0.0",
        "description": "AI-powered hospital information retrieval",
        "endpoints": {
            "query": "POST /query - Query the hospital system",
            "research": "POST /research - Agentic research with tool calling",
            "multi_agent": "POST /multi-agent - Query multiple agents",
            "health": "GET /health - System health check",
            "agents": "GET /agents - List available agents",
            "docs": "GET /docs - Interactive API documentation",
        },
        "supported_languages": ["English", "Spanish", "French", "German"],
        "domains": ["Nursing", "HR", "Pharmacy"]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns status of orchestrator and all agents.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        health = orchestrator.health_check()

        return HealthResponse(
            status="healthy" if health["orchestrator"] == "healthy" else "degraded",
            version="2.0.0",
            timestamp=health["timestamp"],
            orchestrator=health["orchestrator"],
            agents=health["agents"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents", response_model=AgentInfoResponse)
async def get_agents():
    """
    Get information about available agents.
    Returns details about each agent's capabilities and languages.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        info = orchestrator.get_agent_info()
        return AgentInfoResponse(**info)
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main query endpoint.

    Process a user query and route to appropriate agent.
    Supports:
    - Automatic language detection (EN, ES, FR, DE)
    - Intelligent agent routing
    - Document grounding with citations
    - Multi-turn conversations

    Example requests:

    ```json
    {
        "query": "How do I insert an IV line?",
        "user_role": "nurse"
    }
    ```

    ```json
    {
        "query": "¿Cuántos días de vacaciones tengo?",
        "agent_override": "hr"
    }
    ```
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        logger.info(f"[{conversation_id}] Processing query: {request.query[:50]}...")

        # Get conversation history and format for RAG pipeline
        formatted_history = None
        if conversation_id in conversation_history and len(conversation_history[conversation_id]) > 0:
            # Get last N turns from config
            from config import config
            max_turns = config.MAX_CONVERSATION_TURNS

            # Convert to format expected by RAG pipeline
            recent_history = conversation_history[conversation_id][-max_turns:]
            formatted_history = []
            for turn in recent_history:
                formatted_history.append({"role": "user", "content": turn["query"]})
                formatted_history.append({"role": "assistant", "content": turn["answer"]})

            logger.info(f"Including {len(recent_history)} previous turn(s) in context")

        # Process query through orchestrator with conversation history
        result = orchestrator.process_query(
            query=request.query,
            user_role=request.user_role,
            agent_override=request.agent_override,
            conversation_history=formatted_history
        )

        # Check for errors
        if result.get('error'):
            raise HTTPException(
                status_code=500,
                detail=result.get('message', 'Unknown error occurred')
            )

        # Store in conversation history
        if conversation_id not in conversation_history:
            conversation_history[conversation_id] = []

        conversation_history[conversation_id].append({
            "timestamp": result["timestamp"],
            "query": request.query,
            "answer": result["answer"],
            "agent": result["agent"]
        })

        # Build response with both summary and detailed versions
        return QueryResponse(
            conversation_id=conversation_id,
            query=request.query,
            answer=result["answer"],  # Full version (backward compatibility)
            answer_summary=result.get("answer_summary", result["answer"][:200] + "..."),
            answer_detailed=result.get("answer_detailed", result["answer"]),
            agent=result["agent"],
            language=result.get("language", "unknown"),
            total_results=result.get("total_results", 0),
            sources_count=len(result.get("grounding_metadata", [])),
            grounding_metadata=result.get("grounding_metadata", []),
            routing_info=result.get("routing_info", {}),
            timestamp=result["timestamp"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research", response_model=ResearchResponse)
async def research_query(request: ResearchRequest):
    """
    Research endpoint using agentic loop with tool calling.

    This endpoint uses a ReAct-style agent that iteratively:
    1. Reasons about what information is needed
    2. Calls tools to gather information (patient data, nursing protocols, pharmacy info, HR policies)
    3. Observes results and determines next steps
    4. Synthesizes findings into a comprehensive answer

    Perfect for complex multi-step queries that require cross-referencing
    multiple data sources and applying business logic.

    Example use case:
    "What do I need to do today with patient Juan de Marco?"

    The agent will:
    - Get patient details (age, scheduled medications)
    - Check relevant nursing protocols
    - Verify pharmacy inventory and audit compliance
    - Check HR policies if employee-related questions arise
    - Provide actionable recommendations

    Example request:
    ```json
    {
        "query": "What do I need to do today with patient Juan de Marco?"
    }
    ```

    Example response:
    ```json
    {
        "query": "What do I need to do today with patient Juan de Marco?",
        "answer": "Full detailed answer with all information...",
        "answer_summary": "Juan de Marco (65) is scheduled for Oxycodone 5mg, but you must check the pharmacy audit system first—if the audit is overdue (>6 months), hold the medication and notify the physician, pain management team, and pharmacy.",
        "answer_detailed": "Full detailed answer with all information...",
        "agent": "research",
        "iterations": 4,
        "tool_calls": 3,
        "tool_call_history": [...],
        "timestamp": "2025-10-28T..."
    }
    ```

    Response fields:
    - `answer`: Full detailed research answer (same as answer_detailed)
    - `answer_summary`: Concise 2-3 sentence summary perfect for chatbot display
    - `answer_detailed`: Full detailed answer with all context and information
    - Use `answer_summary` for quick chatbot responses, `answer_detailed` for full details
    """
    if not research_agent:
        raise HTTPException(status_code=503, detail="Research agent not initialized")

    try:
        logger.info(f"Research query: {request.query[:50]}...")

        # Perform research using agentic loop
        result = research_agent.research(query=request.query)

        # Check for errors
        if result.get('error'):
            raise HTTPException(
                status_code=500,
                detail=result.get('message', 'Research failed')
            )

        # Build response
        return ResearchResponse(
            query=request.query,
            answer=result["answer"],  # Full detailed answer
            answer_summary=result.get("answer_summary", result["answer"][:200] + "..."),  # Summary for chatbot
            answer_detailed=result.get("answer_detailed", result["answer"]),  # Explicit detailed version
            agent=result["agent"],
            iterations=result.get("iterations", 0),
            tool_calls=result.get("tool_calls", 0),
            tool_call_history=result.get("tool_call_history", []),
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in research query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/multi-agent", response_model=MultiAgentResponse)
async def multi_agent_query(request: MultiAgentRequest):
    """
    Query multiple agents simultaneously.

    Useful for comparing answers across domains or getting comprehensive coverage.

    Example request:
    ```json
    {
        "query": "What are the medication protocols?",
        "agents": ["nursing", "pharmacy"]
    }
    ```
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        logger.info(f"Multi-agent query: {request.query[:50]}...")

        result = orchestrator.multi_agent_query(
            query=request.query,
            agents=request.agents
        )

        return MultiAgentResponse(
            query=result["query"],
            timestamp=result["timestamp"],
            results=result["multi_agent_results"]
        )

    except Exception as e:
        logger.error(f"Error in multi-agent query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history by ID.
    """
    if conversation_id not in conversation_history:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": conversation_history[conversation_id],
        "message_count": len(conversation_history[conversation_id])
    }


@app.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear a conversation history.
    """
    if conversation_id in conversation_history:
        del conversation_history[conversation_id]
        return {"message": f"Conversation {conversation_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Run with: python api.py
    # Or: uvicorn api:app --reload --host 0.0.0.0 --port 8000

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
