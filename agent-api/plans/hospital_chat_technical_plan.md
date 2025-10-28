# Technical Implementation Plan: Multi-Domain, Multi-Format Hospital Chat System

## 1. Project Overview

**Goal:**  
- Enable hospital staff to query **multiple domains** (finance, legal, healthcare protocols) through a **web chat interface**.  
- Each domain corresponds to a **GCS bucket** containing **various file types** (PDFs, Word, Excel, text, HTML, etc.).  
- Vertex AI Search provides **domain-specific semantic search**.  
- ADK orchestrator routes queries to the relevant domain(s) and can **aggregate results across multiple domains**.  
- Answers are **grounded in retrieved documents**, with multi-turn conversation support.  
- Web interface runs on **Google Cloud Run**, accessible to multiple users.  

**Constraints:**  
- Single Google Cloud project.  
- Hackathon-focused → simplicity over optimization.  
- Use **Vertex AI Search** for document retrieval.  
- Multi-turn conversation support.  
- Fully automated pipeline.  

## 2. Architecture

```
[User Web Chat (Browser)]
       ↓
[Cloud Run Service] ← Hosts Web API + Orchestrator
       ↓
[ADK Orchestrator Agent] → Determines which domain(s) to query
       ↓
[ADK Sub-Agents per Domain] → Call Vertex AI Search
       ↓
[Vertex AI Search Index per Domain] → Returns top-N document chunks
       ↓
[Vertex AI Text / Gemini Model] → Generates grounded, multi-turn responses
       ↓
[Cloud Run] → Sends responses + sources to web interface
```

**Key Features:**  
- One orchestrator agent, multiple sub-agents (one per domain).  
- Partial **rule-based + LLM-based routing**.  
- Aggregation of results when queries span multiple domains.  
- Multi-turn memory tracked in ADK.  
- Web interface for multiple users via Cloud Run.  

## 3. Components

### 3.1 Data Storage
- **Buckets per domain:**  
  - `finance-bucket`  
  - `legal-bucket`  
  - `healthcare-bucket`  
- Each bucket can contain **any file format**: PDFs, Word, Excel, CSV, text, HTML.  
- Documents are processed for **text extraction + chunking** before indexing in Vertex AI Search.  

### 3.2 File Ingestion & Chunking Pipeline
**Pipeline Responsibilities:**

1. **Scan bucket** → detect files and file type.  
2. **Extract text** depending on file type:
```python
def extract_text(file_path, file_type):
    if file_type == "pdf":
        # use pdfplumber
    elif file_type == "docx":
        # use python-docx
    elif file_type == "xlsx":
        # use pandas / openpyxl
    elif file_type == "txt":
        # read directly
    elif file_type == "html":
        # use BeautifulSoup
```
3. **Chunk text** (~500–1000 tokens per chunk).  
4. **Add metadata**: bucket name, filename, file type, chunk ID.  
5. **Upload to Vertex AI Search** index for that domain.  

- This approach allows **multiple file formats per bucket**.  
- Copilot can generate this pipeline automatically.  

### 3.3 Vertex AI Search
- **One deployment per domain/bucket.**  
- Index stores **text chunks + metadata**.  
- Supports **semantic retrieval** for queries in the corresponding domain.  
- Returns top-N chunks to be used as context for LLM generation.  

### 3.4 ADK Orchestrator & Sub-Agents
- **Sub-agents** → Wrap Vertex AI Search deployment for each domain.  
- **Orchestrator agent** → Receives user queries and:
  1. Applies **rule-based routing** (keywords, user role).  
  2. Uses **LLM-based classification** if ambiguous.  
  3. Queries **one or more sub-agents**.  
  4. Aggregates results from multiple domains if needed.  
- Tracks **multi-turn conversation context** in ADK.  

### 3.5 LLM Integration
- **Model:** Vertex AI Text / Gemini.  
- **Functionality:** Generate **grounded responses** from top-N retrieved chunks.  
- Includes **multi-turn context** and **source attribution**.  
- Explicitly indicates when information is **not found in documents**.  

### 3.6 Web Interface
- Framework: **Flask** or **FastAPI**.  
- Endpoint: `/chat` → receives query + conversation history → returns LLM response + sources.  
- Hosted on **Cloud Run**:
  - Containerized service.  
  - Auto-scaling for multiple users.  
  - HTTPS endpoint for secure access.  
- Orchestrator and sub-agents are **embedded in the same Cloud Run container**.  

### 3.7 Deployment & Automation
- Copilot generates scripts to:
  1. Create or validate **Vertex AI Search indices**.  
  2. Run **file ingestion + text extraction + chunking**.  
  3. Initialize **sub-agent wrappers**.  
  4. Initialize **ADK orchestrator**.  
  5. Launch **Cloud Run service** with web interface.  

### 3.8 Testing Strategy
- Scripted queries for each domain.  
- Test **multi-turn conversation** and **cross-domain aggregation**.  
- Verify **grounded responses** and **source attribution**.  
- Test web interface with multiple users.  

## 4. Recommendations
- **Keep chunk size consistent** (~500–1000 tokens) for all file types.  
- Include **metadata for each chunk** (bucket, filename, file type) for LLM transparency.  
- Use **hybrid routing**: rule-based first, LLM fallback.  
- Aggregate results across domains only when needed.  
- Run **all orchestrator + sub-agents in a single Cloud Run container** to simplify deployment.  
- Use **service account authentication** for Vertex AI API calls from Cloud Run.  

✅ **Bottom line:**  
- **Buckets per domain** → store multiple file types.  
- **One Vertex AI Search deployment per bucket** → domain-specific retrieval.  
- **ADK orchestrator** → routes and aggregates queries.  
- **Cloud Run web interface** → multi-user, multi-turn chat.  

## 5. Next Steps for Copilot
Copilot can now be used to:

1. Generate **file ingestion pipeline** supporting multiple formats.  
2. Generate **VertexSearchAgent wrappers** per domain.  
3. Generate **sub-agent and orchestrator code** with hybrid routing and aggregation.  
4. Generate **LLM prompt templates and integration code**.  
5. Scaffold **Flask/FastAPI web app** with `/chat` endpoint.  
6. Scaffold **Dockerfile** and `deploy.py` script for Cloud Run deployment.  

> Once fed with this documentation, Copilot should be able to produce a fully modular, production-ready POC for your hackathon system.

