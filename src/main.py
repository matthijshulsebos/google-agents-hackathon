"""
FastAPI web application for the hospital chat system.
"""
import logging
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.config import settings, config
from src.agents.domain_agents import AgentRegistry
from src.agents.orchestrator import OrchestratorAgent
from src.llm.response_generator import ResponseGenerator, ConversationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Multi-Domain Chat System",
    description="AI-powered search across finance, legal, and healthcare domains",
    version="1.0.0"
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
agent_registry: Optional[AgentRegistry] = None
orchestrator: Optional[OrchestratorAgent] = None
response_generator: Optional[ResponseGenerator] = None
conversation_manager: Optional[ConversationManager] = None


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., description="User's question")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn")
    routing_strategy: Optional[str] = Field("keyword", description="Routing strategy: keyword, all, or llm")
    top_k: Optional[int] = Field(5, description="Number of results per domain")


class ChatResponse(BaseModel):
    """Chat response model."""
    conversation_id: str
    query: str
    answer: str
    sources: list
    domains_queried: list
    total_results: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: dict


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global agent_registry, orchestrator, response_generator, conversation_manager
    
    logger.info("Starting Hospital Chat System...")
    
    try:
        # Validate configuration
        if not settings.gcp_project_id:
            logger.warning("GCP_PROJECT_ID not set, some features may not work")
        
        # Initialize agent registry
        logger.info("Initializing agent registry...")
        agent_registry = AgentRegistry(
            project_id=settings.gcp_project_id or config.get("gcp", {}).get("project_id", ""),
            location=settings.gcp_location,
            config=config
        )
        
        # Initialize orchestrator
        logger.info("Initializing orchestrator...")
        orchestrator = OrchestratorAgent(agent_registry)
        
        # Initialize response generator
        logger.info("Initializing response generator...")
        llm_config = config.get("llm", {})
        response_generator = ResponseGenerator(
            project_id=settings.gcp_project_id or config.get("gcp", {}).get("project_id", ""),
            location=settings.gcp_location,
            model_name=llm_config.get("model", "gemini-1.5-pro")
        )
        
        # Initialize conversation manager
        max_history = config.get("api", {}).get("max_conversation_history", 10)
        conversation_manager = ConversationManager(max_history=max_history)
        
        logger.info("Hospital Chat System started successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Hospital Multi-Domain Chat System API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    services = {
        "agent_registry": agent_registry is not None,
        "orchestrator": orchestrator is not None,
        "response_generator": response_generator is not None,
        "conversation_manager": conversation_manager is not None
    }
    
    all_healthy = all(services.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": "1.0.0",
        "services": services
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for querying across domains.
    """
    try:
        # Validate services are initialized
        if not all([orchestrator, response_generator, conversation_manager]):
            raise HTTPException(status_code=503, detail="Services not fully initialized")
        
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get conversation history
        conversation_history = conversation_manager.get_context_for_query(conversation_id)
        
        # Add user query to conversation
        conversation_manager.add_message(conversation_id, "user", request.query)
        
        # Process query through orchestrator
        logger.info(f"Processing query: {request.query[:100]}...")
        search_results = orchestrator.process_query(
            query=request.query,
            conversation_id=conversation_id,
            routing_strategy=request.routing_strategy,
            top_k=request.top_k
        )
        
        # Generate grounded response
        logger.info(f"Generating response with {len(search_results['results'])} results...")
        response_data = response_generator.generate_response(
            query=request.query,
            results=search_results["results"],
            conversation_history=conversation_history
        )
        
        # Add assistant response to conversation
        conversation_manager.add_message(
            conversation_id, 
            "assistant", 
            response_data["answer"],
            metadata={"sources": response_data["sources"]}
        )
        
        return ChatResponse(
            conversation_id=conversation_id,
            query=request.query,
            answer=response_data["answer"],
            sources=response_data["sources"],
            domains_queried=search_results["domains_queried"],
            total_results=search_results["total_results"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/clear")
async def clear_conversation(conversation_id: str):
    """Clear a conversation history."""
    try:
        if conversation_manager:
            conversation_manager.clear_conversation(conversation_id)
            return {"message": f"Conversation {conversation_id} cleared"}
        else:
            raise HTTPException(status_code=503, detail="Conversation manager not initialized")
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/domains")
async def list_domains():
    """List available domains."""
    try:
        if agent_registry:
            domains = list(agent_registry.get_all_agents().keys())
            return {
                "domains": domains,
                "total": len(domains)
            }
        else:
            raise HTTPException(status_code=503, detail="Agent registry not initialized")
    except Exception as e:
        logger.error(f"Error listing domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
