from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

from .auth import setup_adc_from_env
from .orchestrator import Orchestrator
from .config import API_HOST, API_PORT


app = FastAPI(title="Hospital Multi-Domain Chat API")
# Initialize ADC from env before creating the orchestrator (so GCP clients can auth)
try:
    setup_adc_from_env()
except Exception as e:
    print(f"[WARN] Failed to set up ADC from env: {e}")

orchestrator = Orchestrator()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "service": "Hospital Multi-Domain Chat API",
        "status": "running",
        "endpoints": {
            "health": "/healthz",
            "chat": "POST /chat"
        }
    }


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Stable identifier per user/session")
    query: str
    domains: Optional[List[str]] = Field(None, description="Optional explicit domains: nursing, pharmacy, po")


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    domains: List[str]
    retrieval: Dict[str, int]


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = orchestrator.answer(req.session_id, req.query, req.domains)
    return result


# For local run: uvicorn app.web:app --host 0.0.0.0 --port 8080
