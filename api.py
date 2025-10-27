#!/usr/bin/env python3
"""
FastAPI HTTP API for Hospital Multi-Agent RAG System
Uses the current orchestrator.py and RAG pipeline
"""
import logging
import uuid
from typing import Optional, Dict, Any
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
    answer: str = Field(..., description="Generated answer")
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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global orchestrator

    logger.info("Starting Hospital Multi-Agent RAG System...")

    try:
        # Initialize orchestrator
        logger.info("Initializing HospitalOrchestrator...")
        orchestrator = HospitalOrchestrator()

        logger.info("Hospital Multi-Agent RAG System started successfully!")

        # Run health check
        health = orchestrator.health_check()
        logger.info(f"Orchestrator status: {health['orchestrator']}")
        for agent_name, agent_status in health['agents'].items():
            if agent_status.get('healthy'):
                logger.info(f"  ✓ {agent_name} agent: {agent_status.get('implementation', 'ready')}")
            else:
                logger.warning(f"  ✗ {agent_name} agent: {agent_status.get('error', 'not healthy')}")

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

        # Process query through orchestrator
        result = orchestrator.process_query(
            query=request.query,
            user_role=request.user_role,
            agent_override=request.agent_override
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

        # Build response
        return QueryResponse(
            conversation_id=conversation_id,
            query=request.query,
            answer=result["answer"],
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
