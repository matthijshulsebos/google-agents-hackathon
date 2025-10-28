# 🏥 Hospital AI Assistant# 🏥 Hospital AI Agent - Multi-Domain Search System# Hospital Multi-Domain Chat System



> Multi-domain intelligent chat assistant powered by Vertex AI Search and Gemini



An AI-powered assistant that helps hospital staff find information across nursing, pharmacy, and HR domains using natural language conversations. Built with Google's Agent Development Kit (ADK), Vertex AI Search, and Gemini 2.0 Flash.An AI-powered agent built with **Google's Agent Development Kit (ADK)** that intelligently searches across nursing, pharmacy, and HR domains using **Vertex AI Search** and **Gemini**.An AI-powered search and chat system for hospital staff to query across multiple domains (nursing, pharmacy, and HR) using natural language.



## ✨ Features



- 🤖 **Intelligent Routing** - Gemini automatically routes queries to the right domain## 🌟 Features## Features

- 🔍 **Multi-Domain Search** - Query across nursing, pharmacy, and HR knowledge bases

- 📚 **Grounded Responses** - All answers cite specific source documents

- 💬 **Conversational** - Maintains context across multiple turns

- 📄 **Multi-Format Support** - Indexes PDF, Word, Excel, CSV, HTML, and text files- 🤖 **True AI Agent**: Uses Gemini to autonomously decide which domains to search- 🔍 **Multi-Domain Search**: Query across nursing, pharmacy, and HR domains

- ⚡ **Fast Deployment** - Terminal, web, and API interfaces ready to use

- 🔍 **Multi-Domain Search**: Searches across nursing, pharmacy, and HR datastores- 🤖 **AI-Powered Responses**: Grounded answers using Vertex AI Gemini

## 🏗️ Architecture

- 📚 **Grounded Responses**: All answers cite specific source documents- 💬 **Multi-Turn Conversations**: Context-aware chat with conversation history

```

User Query: "How do I insert a peripheral IV?"- 💬 **Conversational Memory**: Remembers context across multiple turns- 📄 **Multiple File Formats**: Supports PDFs, Word, Excel, CSV, HTML, and text files

     ↓

┌────────────────────────────────────────┐- 🛠️ **Tool-Based Architecture**: Agent uses specialized search tools for each domain- 🎯 **Smart Routing**: Keyword-based and LLM-based query routing

│  Gemini 2.0 Flash (ADK Agent)         │

│  • Analyzes query                      │- ⚡ **Powered by Vertex AI**: Uses Vertex AI Search for semantic retrieval- 🔗 **Source Attribution**: All answers cite their source documents

│  • Routes to nursing domain            │

│  • Extracts search terms               │- ☁️ **Cloud Run Deployment**: Scalable, serverless deployment on Google Cloud

└────────────────┬───────────────────────┘

                 ↓## 🏗️ Architecture

┌────────────────────────────────────────┐

│  Vertex AI Search (3 Datastores)      │## Architecture

│  • nursing-datastore-v6                │

│  • pharmacy-datastore-v6               │```

│  • po-datastore-v6 (HR)                │

└────────────────┬───────────────────────┘User Query```

                 ↓

┌────────────────────────────────────────┐    ↓User → Cloud Run Web API → Orchestrator Agent

│  Response Synthesis                    │

│  • Retrieves document content          │ADK Agent (Gemini 1.5 Pro)                              ↓

│  • Gemini synthesizes answer           │

│  • Returns with source citations       │    ├─ Decides which domain(s) to search                    Domain-Specific Agents

└────────────────────────────────────────┘

```    ├─ Uses search tools:                    (Nursing, Pharmacy, HR)



## 🚀 Quick Start    │   ├─ search_nursing_domain()                              ↓



### Prerequisites    │   ├─ search_pharmacy_domain()                    Vertex AI Search Indices



- Python 3.12+    │   └─ search_hr_domain()                              ↓

- Google Cloud Project with:

  - Vertex AI API enabled    ↓                      Vertex AI Gemini

  - Discovery Engine API enabled

- GCS buckets with your documents:Domain Agents (NursingAgent, PharmacyAgent, HRAgent)                              ↓

  - `data-nursing`

  - `data-pharmacy`    ↓                    Grounded Response with Sources

  - `data-po`

Vertex AI Search Datastores```

### Installation

    ├─ nursing-datastore-v2

```bash

# Clone the repository    ├─ pharmacy-datastore-v2## Your Existing Buckets

cd /home/mat/Documents/google-hackathon

    └─ po-datastore-v2

# Create virtual environment

python3.12 -m venv venv    ↓✅ This system works with your **existing GCS buckets**:

source venv/bin/activate

Gemini synthesizes grounded answer with sources- `nursing` - Nursing policies, procedures, protocols

# Install dependencies

pip install -r requirements.txt```- `pharmacy` - Medication information, formularies  



# Configure environment- `po` - HR (Human Resources) documents, personnel files

cp .env.example .env

# Edit .env with your GCP_PROJECT_ID and GCP_LOCATION## 📦 What's Inside

```

The system **reads** your files and creates **search indices** (datastores) to enable AI-powered search. Your original files remain unchanged. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for details.

### Setup (One-Time)

### Infrastructure (Shared)

```bash

# Authenticate with Google Cloud- **GCS Buckets**: `data-nursing`, `data-pharmacy`, `data-po` (your existing files)## Prerequisites

gcloud auth application-default login

- **Vertex AI Search Datastores**: Searchable indices for each domain

# Create Vertex AI Search datastores

python scripts/setup_datastores.py --all- **Domain Agents**: Specialized search agents that query Vertex Search- Google Cloud Platform account



# Create Search Apps (engines)- Python 3.11+

python scripts/setup_search_apps.py --all

### ADK Agent- Docker (for deployment)

# Index your documents

python scripts/ingest_documents.py --all- **Agent**: `src/adk_agent/hospital_agent.py`- Google Cloud SDK (`gcloud` CLI)

# Wait 2-3 minutes for indexing to complete

```- **Tools**: Functions that agent can call to search each domain



## 💬 Using the Assistant- **System Instructions**: Guides agent behavior and response style## Setup



### Option 1: Terminal Chat (Instant)



```bash## 🚀 Quick Start### 1. Clone and Configure

python interactive_chat.py

```



Perfect for quick testing and command-line usage.### 1. Prerequisites```bash



### Option 2: Web Interface (Recommended)cd /home/mat/Documents/google-hackathon



```bash```bash

# Install Streamlit

pip install streamlit# Ensure you have:# Copy environment template



# Launch web app- Python 3.12cp .env.example .env

streamlit run app.py

```- Google Cloud Project with:



Opens at `http://localhost:8501` with a beautiful chat interface.  - Vertex AI API enabled# Edit .env with your GCP project details



### Option 3: REST API  - Discovery Engine API enablednano .env



```bash  - Your buckets: data-nursing, data-pharmacy, data-po```

# Install Flask

pip install flask flask-cors```



# Start API server### 2. Install Dependencies

python api.py

```### 2. Setup Environment



API available at `http://localhost:5000````bash



**Example API call:**```bash# Create virtual environment

```bash

curl -X POST http://localhost:5000/api/chat \# Clone and setuppython -m venv venv

  -H "Content-Type: application/json" \

  -d '{"message": "How do I insert a peripheral IV?"}'git clone <your-repo>source venv/bin/activate

```

cd google-hackathon

## 📝 Example Queries

# Install requirements

**Nursing Domain:**

- "How do I insert a peripheral IV?"# Create virtual environment with Python 3.12pip install -r requirements.txt

- "What's the procedure for catheter insertion?"

- "Tell me about central line dressing changes"python3.12 -m venv venv```

- "What are the steps for blood glucose monitoring?"

source venv/bin/activate

**Pharmacy Domain:**

- "What medications are in the inventory?"### 3. Configure Google Cloud

- "Tell me about drug storage requirements"

# Install dependencies

**HR Domain:**

- "What are the controlled medication protocols?"pip install -r requirements.txtEdit `config.yaml` with your project details:

- "Tell me about employee policies"

- Project ID

## 📁 Project Structure

# Configure environment- Location

```

google-hackathon/cp .env.example .env- Bucket names

├── src/

│   ├── adk_agent/# Edit .env with your GCP_PROJECT_ID and bucket names- Datastore IDs

│   │   └── hospital_agent_vertex.py    # Main ADK agent with Gemini

│   ├── agents/```

│   │   ├── domain_agents.py            # Domain-specific agent wrappers

│   │   └── orchestrator.py             # Agent registry### 4. Set Up Infrastructure

│   ├── ingestion/

│   │   ├── document_processor.py       # Text extraction & chunking### 3. Authenticate with GCP

│   │   └── vertex_search.py            # Vertex Search indexing/retrieval

│   └── config.py                       # Configuration management```bash

│

├── scripts/```bash# Authenticate with GCP

│   ├── setup_datastores.py             # Create Vertex AI Search datastores

│   ├── setup_search_apps.py            # Create Search Apps (engines)gcloud auth application-default logingcloud auth login

│   ├── ingest_documents.py             # Index documents from GCS

│   ├── list_datastores.py              # List existing datastoresgcloud auth application-default set-quota-project YOUR_PROJECT_IDgcloud config set project YOUR_PROJECT_ID

│   └── delete_datastores.py            # Cleanup utility

│```

├── tests/

│   ├── test_api.py                     # API tests# Create GCS buckets

│   └── test_adk_integration.py         # End-to-end integration tests

│### 4. Create Datastores (One-Time Setup)python scripts/setup_buckets.py --all

├── interactive_chat.py                 # Terminal chat interface

├── app.py                              # Streamlit web interface

├── api.py                              # Flask REST API

│```bash# Create Vertex AI Search datastores

├── config.yaml                         # Domain configuration

├── requirements.txt                    # Python dependenciesexport PYTHONPATH="$PYTHONPATH:$(pwd)"python scripts/setup_datastores.py --all

├── Dockerfile                          # Container definition

│python scripts/setup_datastores.py --all

├── README.md                           # This file

├── ARCHITECTURE.md                     # Technical architecture details```# Your buckets already have documents - just ingest them into search indices

└── DEPLOYMENT.md                       # Production deployment guide

```python scripts/ingest_documents.py --all



## ⚙️ ConfigurationThis creates three Vertex AI Search datastores in your GCP project.```



### Environment Variables (`.env`)



```bash### 5. Index Your Documents## Running Locally

# Google Cloud Configuration

GCP_PROJECT_ID=your-project-id

GCP_LOCATION=eu  # or us-central1, etc.

```bash```bash

# GCS Buckets (your existing buckets)

NURSING_BUCKET=data-nursingpython scripts/ingest_documents.py --all# Start the API server

PHARMACY_BUCKET=data-pharmacy

PO_BUCKET=data-po```python src/main.py



# Datastore IDs

NURSING_DATASTORE_ID=nursing-datastore-v6

PHARMACY_DATASTORE_ID=pharmacy-datastore-v6This reads files from your buckets, processes them, and indexes into datastores.  # In another terminal, run tests

PO_DATASTORE_ID=po-datastore-v6

```**Time**: 10-30 minutes depending on document count.python tests/test_api.py



### Application Configuration (`config.yaml`)```



- **Chunking**: 800 tokens per chunk, 200 token overlap### 6. Test the ADK Agent

- **Search**: Top-5 results per domain

- **Model**: Gemini 2.0 Flash (temperature: 0.2)The API will be available at `http://localhost:8080`



## 🧪 Testing```bash



```bashpython src/adk_agent/hospital_agent.py## API Endpoints

# Run integration tests

python tests/test_adk_integration.py```



# Test individual components### Chat

python -c "

from src.ingestion.vertex_search import VertexSearchRetrieverThis runs test queries to verify the agent works!```bash

from src.config import settings

POST /chat

retriever = VertexSearchRetriever(

    settings.gcp_project_id,## 💬 Using the Agent{

    settings.gcp_location,

    settings.nursing_datastore_id  "query": "What is the hospital budget for equipment?",

)

results = retriever.search('blood glucose monitoring')### Python API  "conversation_id": "optional-conversation-id",

print(f'Found {len(results)} results')

"  "routing_strategy": "keyword",  # keyword, all, or llm

```

```python  "top_k": 5

## 🚢 Production Deployment

from src.adk_agent.hospital_agent import chat_with_agent}

### Cloud Run (Recommended)

```

```bash

# Build and deploy# Ask a question

gcloud builds submit --tag gcr.io/PROJECT_ID/hospital-assistant

gcloud run deploy hospital-assistant \result = chat_with_agent("What are the nursing protocols for patient intake?")### Health Check

  --image gcr.io/PROJECT_ID/hospital-assistant \

  --platform managed \```bash

  --region us-central1 \

  --allow-unauthenticatedprint(result["answer"])GET /health

```

print(f"Sources: {len(result['sources'])} documents")```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide including:

- Google App Engine deployment

- Vertex AI Endpoints

- Security best practices# Continue conversation### List Domains

- Monitoring and scaling

result = chat_with_agent(```bash

## 📊 Cost Estimates

    "What about medication procedures?",GET /domains

**Development/Testing:**

- Vertex AI Search: ~$0 (free tier)    chat_history=result["chat_history"]```

- Gemini API: ~$10-50/month

- **Total: ~$10-50/month**)



**Production (10k queries/month):**```### Clear Conversation

- Vertex AI Search: ~$100/month

- Gemini API: ~$200-500/month```bash

- Cloud Run: ~$50/month

- **Total: ~$370-670/month**### Example QueriesPOST /chat/clear?conversation_id=<id>



## 🔧 Maintenance```



### Regular Tasks```python



- **Weekly**: Monitor search quality, update documents# Single domain## Deployment to Cloud Run

- **Monthly**: Review usage patterns, optimize queries

- **Quarterly**: Retrain/update datastores with new content"What are the nursing shift change procedures?"



### Useful Commands```bash



```bash# Multiple domains# Set environment variables

# List all datastores

python scripts/list_datastores.py"What are the HR policies for hiring pharmacy staff?"export GCP_PROJECT_ID="your-project-id"



# Re-index documentsexport GCP_LOCATION="us-central1"

python scripts/ingest_documents.py --all

# Cross-domain reasoningexport FINANCE_BUCKET="finance-bucket"

# Delete and recreate datastores (careful!)

python scripts/delete_datastores.py --all"Compare the training requirements for nursing vs pharmacy staff"export LEGAL_BUCKET="legal-bucket"

python scripts/setup_datastores.py --all

``````export HEALTHCARE_BUCKET="healthcare-bucket"



## 🐛 Troubleshootingexport FINANCE_DATASTORE_ID="finance-datastore"



**Rate limit errors (429)?**## 📁 Project Structureexport LEGAL_DATASTORE_ID="legal-datastore"

- Wait 10-30 seconds between queries

- Gemini API has quota limits in free tierexport HEALTHCARE_DATASTORE_ID="healthcare-datastore"



**No search results?**```

- Ensure documents are indexed: `python scripts/ingest_documents.py --all`

- Wait 2-3 minutes for indexing to completegoogle-hackathon/# Deploy

- Check datastore IDs match in `.env`

├── src/chmod +x scripts/deploy.sh

**Import errors?**

- Reinstall dependencies: `pip install -r requirements.txt --upgrade`│   ├── adk_agent/./scripts/deploy.sh

- Verify Python 3.12+ is being used

│   │   └── hospital_agent.py      # Main ADK agent implementation```

**Content not returned in search?**

- We fetch full documents using `DocumentServiceClient.get_document()`│   ├── agents/

- Ensure regional API endpoint matches datastore location

│   │   └── domain_agents.py       # NursingAgent, PharmacyAgent, HRAgent## Project Structure

## 📚 Additional Documentation

│   ├── ingestion/

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed technical architecture

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide│   │   ├── document_processor.py  # Text extraction & chunking```

- **API Endpoints** - See docstrings in `api.py`

│   │   └── vertex_search.py       # Vertex Search indexing/retrievalgoogle-hackathon/

## 🎯 How It Works

│   └── config.py                  # Configuration management├── src/

1. **Document Ingestion**

   - Reads files from GCS buckets (CSV, PDF, DOCX, etc.)├── scripts/│   ├── main.py                    # FastAPI application

   - Extracts and chunks text (800 tokens with 200 overlap)

   - Indexes into Vertex AI Search datastores│   ├── setup_datastores.py        # Create Vertex AI Search datastores│   ├── config.py                  # Configuration management



2. **Query Processing**│   ├── ingest_documents.py        # Index documents from buckets│   ├── agents/

   - User asks a natural language question

   - Gemini analyzes query and routes to appropriate domain(s)│   ├── delete_datastores.py       # Delete datastores (cleanup)│   │   ├── domain_agents.py       # Domain-specific search agents

   - Executes search tool functions

│   └── list_datastores.py         # List existing datastores│   │   └── orchestrator.py        # Query routing and aggregation

3. **Search & Retrieval**

   - Vertex AI Search finds semantically relevant documents├── config.yaml                    # Domain and retrieval configuration│   ├── ingestion/

   - Full document content fetched via Document Service API

   - Returns top-k results with metadata├── .env                           # Environment variables (GCP project, buckets)│   │   ├── document_processor.py  # Multi-format text extraction



4. **Response Generation**└── requirements.txt               # Python dependencies│   │   └── vertex_search.py       # Vertex AI Search integration

   - Gemini receives search results with full content

   - Synthesizes grounded answer from retrieved documents```│   └── llm/

   - Cites specific sources

│       └── response_generator.py  # Gemini response generation

## 🤝 Contributing

## 🔧 Configuration├── scripts/

This is a hackathon project. For production use:

- Add authentication (OAuth 2.0, IAM)│   ├── setup_buckets.py          # Create GCS buckets

- Implement rate limiting

- Add monitoring and alerting### `.env` file│   ├── setup_datastores.py       # Create search datastores

- Use Secret Manager for credentials

- Enable audit logging│   ├── ingest_documents.py       # Ingest documents to search



## 📄 License```bash│   └── deploy.sh                 # Deploy to Cloud Run



MIT License# Google Cloud Configuration├── tests/



## 🙏 AcknowledgmentsGCP_PROJECT_ID=your-project-id│   └── test_api.py               # Integration tests



Built with:GCP_LOCATION=eu  # or us, asia, etc.├── config.yaml                    # Application configuration

- [Google Vertex AI Search](https://cloud.google.com/vertex-ai-search-and-conversation)

- [Gemini 2.0 Flash](https://ai.google.dev/models/gemini)├── requirements.txt              # Python dependencies

- [Google Agent Development Kit (ADK)](https://cloud.google.com/vertex-ai/docs/agent-builder)

# Bucket Names (your existing buckets)├── Dockerfile                    # Container definition

---

NURSING_BUCKET=data-nursing└── README.md                     # This file

**Ready to start?** Run `python interactive_chat.py` now! 🚀

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
