# 🏥 Hospital AI Agent - Multi-Domain Search System# Hospital Multi-Domain Chat System



An AI-powered agent built with **Google's Agent Development Kit (ADK)** that intelligently searches across nursing, pharmacy, and HR domains using **Vertex AI Search** and **Gemini**.An AI-powered search and chat system for hospital staff to query across multiple domains (nursing, pharmacy, and HR) using natural language.



## 🌟 Features## Features



- 🤖 **True AI Agent**: Uses Gemini to autonomously decide which domains to search- 🔍 **Multi-Domain Search**: Query across nursing, pharmacy, and HR domains

- 🔍 **Multi-Domain Search**: Searches across nursing, pharmacy, and HR datastores- 🤖 **AI-Powered Responses**: Grounded answers using Vertex AI Gemini

- 📚 **Grounded Responses**: All answers cite specific source documents- 💬 **Multi-Turn Conversations**: Context-aware chat with conversation history

- 💬 **Conversational Memory**: Remembers context across multiple turns- 📄 **Multiple File Formats**: Supports PDFs, Word, Excel, CSV, HTML, and text files

- 🛠️ **Tool-Based Architecture**: Agent uses specialized search tools for each domain- 🎯 **Smart Routing**: Keyword-based and LLM-based query routing

- ⚡ **Powered by Vertex AI**: Uses Vertex AI Search for semantic retrieval- 🔗 **Source Attribution**: All answers cite their source documents

- ☁️ **Cloud Run Deployment**: Scalable, serverless deployment on Google Cloud

## 🏗️ Architecture

## Architecture

```

User Query```

    ↓User → Cloud Run Web API → Orchestrator Agent

ADK Agent (Gemini 1.5 Pro)                              ↓

    ├─ Decides which domain(s) to search                    Domain-Specific Agents

    ├─ Uses search tools:                    (Nursing, Pharmacy, HR)

    │   ├─ search_nursing_domain()                              ↓

    │   ├─ search_pharmacy_domain()                    Vertex AI Search Indices

    │   └─ search_hr_domain()                              ↓

    ↓                      Vertex AI Gemini

Domain Agents (NursingAgent, PharmacyAgent, HRAgent)                              ↓

    ↓                    Grounded Response with Sources

Vertex AI Search Datastores```

    ├─ nursing-datastore-v2

    ├─ pharmacy-datastore-v2## Your Existing Buckets

    └─ po-datastore-v2

    ↓✅ This system works with your **existing GCS buckets**:

Gemini synthesizes grounded answer with sources- `nursing` - Nursing policies, procedures, protocols

```- `pharmacy` - Medication information, formularies  

- `po` - HR (Human Resources) documents, personnel files

## 📦 What's Inside

The system **reads** your files and creates **search indices** (datastores) to enable AI-powered search. Your original files remain unchanged. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for details.

### Infrastructure (Shared)

- **GCS Buckets**: `data-nursing`, `data-pharmacy`, `data-po` (your existing files)## Prerequisites

- **Vertex AI Search Datastores**: Searchable indices for each domain

- **Domain Agents**: Specialized search agents that query Vertex Search- Google Cloud Platform account

- Python 3.11+

### ADK Agent- Docker (for deployment)

- **Agent**: `src/adk_agent/hospital_agent.py`- Google Cloud SDK (`gcloud` CLI)

- **Tools**: Functions that agent can call to search each domain

- **System Instructions**: Guides agent behavior and response style## Setup



## 🚀 Quick Start### 1. Clone and Configure



### 1. Prerequisites```bash

cd /home/mat/Documents/google-hackathon

```bash

# Ensure you have:# Copy environment template

- Python 3.12cp .env.example .env

- Google Cloud Project with:

  - Vertex AI API enabled# Edit .env with your GCP project details

  - Discovery Engine API enablednano .env

  - Your buckets: data-nursing, data-pharmacy, data-po```

```

### 2. Install Dependencies

### 2. Setup Environment

```bash

```bash# Create virtual environment

# Clone and setuppython -m venv venv

git clone <your-repo>source venv/bin/activate

cd google-hackathon

# Install requirements

# Create virtual environment with Python 3.12pip install -r requirements.txt

python3.12 -m venv venv```

source venv/bin/activate

### 3. Configure Google Cloud

# Install dependencies

pip install -r requirements.txtEdit `config.yaml` with your project details:

- Project ID

# Configure environment- Location

cp .env.example .env- Bucket names

# Edit .env with your GCP_PROJECT_ID and bucket names- Datastore IDs

```

### 4. Set Up Infrastructure

### 3. Authenticate with GCP

```bash

```bash# Authenticate with GCP

gcloud auth application-default logingcloud auth login

gcloud auth application-default set-quota-project YOUR_PROJECT_IDgcloud config set project YOUR_PROJECT_ID

```

# Create GCS buckets

### 4. Create Datastores (One-Time Setup)python scripts/setup_buckets.py --all



```bash# Create Vertex AI Search datastores

export PYTHONPATH="$PYTHONPATH:$(pwd)"python scripts/setup_datastores.py --all

python scripts/setup_datastores.py --all

```# Your buckets already have documents - just ingest them into search indices

python scripts/ingest_documents.py --all

This creates three Vertex AI Search datastores in your GCP project.```



### 5. Index Your Documents## Running Locally



```bash```bash

python scripts/ingest_documents.py --all# Start the API server

```python src/main.py



This reads files from your buckets, processes them, and indexes into datastores.  # In another terminal, run tests

**Time**: 10-30 minutes depending on document count.python tests/test_api.py

```

### 6. Test the ADK Agent

The API will be available at `http://localhost:8080`

```bash

python src/adk_agent/hospital_agent.py## API Endpoints

```

### Chat

This runs test queries to verify the agent works!```bash

POST /chat

## 💬 Using the Agent{

  "query": "What is the hospital budget for equipment?",

### Python API  "conversation_id": "optional-conversation-id",

  "routing_strategy": "keyword",  # keyword, all, or llm

```python  "top_k": 5

from src.adk_agent.hospital_agent import chat_with_agent}

```

# Ask a question

result = chat_with_agent("What are the nursing protocols for patient intake?")### Health Check

```bash

print(result["answer"])GET /health

print(f"Sources: {len(result['sources'])} documents")```



# Continue conversation### List Domains

result = chat_with_agent(```bash

    "What about medication procedures?",GET /domains

    chat_history=result["chat_history"]```

)

```### Clear Conversation

```bash

### Example QueriesPOST /chat/clear?conversation_id=<id>

```

```python

# Single domain## Deployment to Cloud Run

"What are the nursing shift change procedures?"

```bash

# Multiple domains# Set environment variables

"What are the HR policies for hiring pharmacy staff?"export GCP_PROJECT_ID="your-project-id"

export GCP_LOCATION="us-central1"

# Cross-domain reasoningexport FINANCE_BUCKET="finance-bucket"

"Compare the training requirements for nursing vs pharmacy staff"export LEGAL_BUCKET="legal-bucket"

```export HEALTHCARE_BUCKET="healthcare-bucket"

export FINANCE_DATASTORE_ID="finance-datastore"

## 📁 Project Structureexport LEGAL_DATASTORE_ID="legal-datastore"

export HEALTHCARE_DATASTORE_ID="healthcare-datastore"

```

google-hackathon/# Deploy

├── src/chmod +x scripts/deploy.sh

│   ├── adk_agent/./scripts/deploy.sh

│   │   └── hospital_agent.py      # Main ADK agent implementation```

│   ├── agents/

│   │   └── domain_agents.py       # NursingAgent, PharmacyAgent, HRAgent## Project Structure

│   ├── ingestion/

│   │   ├── document_processor.py  # Text extraction & chunking```

│   │   └── vertex_search.py       # Vertex Search indexing/retrievalgoogle-hackathon/

│   └── config.py                  # Configuration management├── src/

├── scripts/│   ├── main.py                    # FastAPI application

│   ├── setup_datastores.py        # Create Vertex AI Search datastores│   ├── config.py                  # Configuration management

│   ├── ingest_documents.py        # Index documents from buckets│   ├── agents/

│   ├── delete_datastores.py       # Delete datastores (cleanup)│   │   ├── domain_agents.py       # Domain-specific search agents

│   └── list_datastores.py         # List existing datastores│   │   └── orchestrator.py        # Query routing and aggregation

├── config.yaml                    # Domain and retrieval configuration│   ├── ingestion/

├── .env                           # Environment variables (GCP project, buckets)│   │   ├── document_processor.py  # Multi-format text extraction

└── requirements.txt               # Python dependencies│   │   └── vertex_search.py       # Vertex AI Search integration

```│   └── llm/

│       └── response_generator.py  # Gemini response generation

## 🔧 Configuration├── scripts/

│   ├── setup_buckets.py          # Create GCS buckets

### `.env` file│   ├── setup_datastores.py       # Create search datastores

│   ├── ingest_documents.py       # Ingest documents to search

```bash│   └── deploy.sh                 # Deploy to Cloud Run

# Google Cloud Configuration├── tests/

GCP_PROJECT_ID=your-project-id│   └── test_api.py               # Integration tests

GCP_LOCATION=eu  # or us, asia, etc.├── config.yaml                    # Application configuration

├── requirements.txt              # Python dependencies

# Bucket Names (your existing buckets)├── Dockerfile                    # Container definition

NURSING_BUCKET=data-nursing└── README.md                     # This file

PHARMACY_BUCKET=data-pharmacy```

PO_BUCKET=data-po

## Usage Examples

# Datastore IDs

NURSING_DATASTORE_ID=nursing-datastore-v2### Single Domain Query

PHARMACY_DATASTORE_ID=pharmacy-datastore-v2```python

PO_DATASTORE_ID=po-datastore-v2import requests

```

response = requests.post("http://localhost:8080/chat", json={

### `config.yaml`    "query": "What are the nursing shift handoff procedures?",

    "routing_strategy": "keyword"

Defines chunking strategy, retrieval parameters, and domain mappings.})

print(response.json()["answer"])

## 🎯 How It Works```



### 1. Document Ingestion### Multi-Turn Conversation

- Reads files from GCS buckets (PDF, Word, Excel, CSV, HTML)```python

- Extracts text using specialized libraries# First message

- Chunks into 800-token pieces with 200-token overlapresponse1 = requests.post("http://localhost:8080/chat", json={

- Indexes into Vertex AI Search datastores    "query": "What are patient intake procedures?"

})

### 2. Agent Decision-Makingconv_id = response1.json()["conversation_id"]

- User asks a question

- Gemini-powered agent analyzes the query# Follow-up with context

- Agent decides which domain tool(s) to callresponse2 = requests.post("http://localhost:8080/chat", json={

- Can call multiple tools if needed    "query": "What documents are needed for that?",

    "conversation_id": conv_id

### 3. Search & Retrieval})

- Domain agents query Vertex AI Search```

- Semantic search finds relevant document chunks

- Returns top-k results with metadata### Cross-Domain Query

```python

### 4. Response Generationresponse = requests.post("http://localhost:8080/chat", json={

- Agent receives search results    "query": "What are the purchasing procedures for pharmacy medications?",

- Gemini synthesizes a grounded answer    "routing_strategy": "keyword"

- Cites specific source documents})

- Returns answer with sources# Will query both pharmacy and po (HR) domains

```

## 🧪 Testing

## Supported File Formats

```bash

# Test individual components- **PDF** (.pdf)

python -m pytest tests/- **Word** (.docx, .doc)

- **Excel** (.xlsx, .xls)

# Test ADK agent- **CSV** (.csv)

python src/adk_agent/hospital_agent.py- **HTML** (.html, .htm)

- **Text** (.txt)

# Test domain agents

python -c "## Configuration

from src.agents.domain_agents import AgentRegistry

from src.config import settings, config### Chunking Parameters

- `chunk_size`: 800 tokens (configurable in config.yaml)

registry = AgentRegistry(settings.gcp_project_id, settings.gcp_location, config)- `chunk_overlap`: 200 tokens

agent = registry.get_agent('nursing')- `min_chunk_size`: 100 tokens

results = agent.search('patient intake procedures')

print(f'Found {len(results)} results')### LLM Parameters

"- Model: `gemini-1.5-pro`

```- Temperature: 0.2 (factual responses)

- Max output tokens: 2048

## 📚 Documentation

### Routing Strategies

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions- `keyword`: Route based on domain-specific keywords (default)

- **[ADK_APPROACH.md](ADK_APPROACH.md)** - Understanding the ADK architecture- `all`: Query all domains

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference- `llm`: Use LLM for intelligent routing (planned)

- **[VISUAL_GUIDE.md](VISUAL_GUIDE.md)** - Visual architecture diagrams

## Troubleshooting

## 🚢 Deployment

### Authentication Errors

### Option 1: Local Development```bash

Run the agent locally for testing and development.gcloud auth application-default login

```

### Option 2: Cloud Run

Deploy the agent as a web service (requires wrapping in FastAPI/Flask).### Missing Dependencies

```bash

### Option 3: Vertex AI Agent Builderpip install -r requirements.txt --upgrade

Export the agent configuration to Vertex AI Agent Builder for managed hosting.```



## 📝 License### Datastore Not Found

Ensure datastores are created and IDs match configuration:

MIT License```bash

python scripts/setup_datastores.py --all

## 🎓 Learn More```



- [Google Agent Development Kit](https://cloud.google.com/vertex-ai/docs/agent-builder)## Security Considerations

- [Vertex AI Search](https://cloud.google.com/vertex-ai-search-and-conversation)

- [Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)- Enable authentication for production deployments

- Use service accounts with minimal permissions

---- Store sensitive configuration in Secret Manager

- Enable CORS only for trusted origins

**Built with ❤️ using Google Cloud Vertex AI**- Implement rate limiting


## Future Enhancements

- [ ] LLM-based query routing
- [ ] Advanced multi-domain aggregation
- [ ] User authentication and role-based access
- [ ] Query history and analytics
- [ ] Streaming responses
- [ ] Document upload via API
- [ ] Real-time indexing updates

## License

This project is created for hackathon purposes.

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.
