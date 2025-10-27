# Hospital Multi-Domain Chat System

An AI-powered search and chat system for hospital staff to query across multiple domains (finance, legal, and healthcare protocols) using natural language.

## Features

- 🔍 **Multi-Domain Search**: Query across finance, legal, and healthcare domains
- 🤖 **AI-Powered Responses**: Grounded answers using Vertex AI Gemini
- 💬 **Multi-Turn Conversations**: Context-aware chat with conversation history
- 📄 **Multiple File Formats**: Supports PDFs, Word, Excel, CSV, HTML, and text files
- 🎯 **Smart Routing**: Keyword-based and LLM-based query routing
- 🔗 **Source Attribution**: All answers cite their source documents
- ☁️ **Cloud Run Deployment**: Scalable, serverless deployment on Google Cloud

## Architecture

```
User → Cloud Run Web API → Orchestrator Agent
                              ↓
                    Domain-Specific Agents
                    (Finance, Legal, Healthcare)
                              ↓
                    Vertex AI Search Indices
                              ↓
                      Vertex AI Gemini
                              ↓
                    Grounded Response with Sources
```

## Prerequisites

- Google Cloud Platform account
- Python 3.11+
- Docker (for deployment)
- Google Cloud SDK (`gcloud` CLI)

## Setup

### 1. Clone and Configure

```bash
cd /home/mat/Documents/google-hackathon

# Copy environment template
cp .env.example .env

# Edit .env with your GCP project details
nano .env
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Google Cloud

Edit `config.yaml` with your project details:
- Project ID
- Location
- Bucket names
- Datastore IDs

### 4. Set Up Infrastructure

```bash
# Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create GCS buckets
python scripts/setup_buckets.py --all

# Create Vertex AI Search datastores
python scripts/setup_datastores.py --all

# Upload documents to buckets (use GCS console or gsutil)
gsutil cp -r /path/to/finance/docs gs://finance-bucket/
gsutil cp -r /path/to/legal/docs gs://legal-bucket/
gsutil cp -r /path/to/healthcare/docs gs://healthcare-bucket/

# Ingest documents into search indices
python scripts/ingest_documents.py --all
```

## Running Locally

```bash
# Start the API server
python src/main.py

# In another terminal, run tests
python tests/test_api.py
```

The API will be available at `http://localhost:8080`

## API Endpoints

### Chat
```bash
POST /chat
{
  "query": "What is the hospital budget for equipment?",
  "conversation_id": "optional-conversation-id",
  "routing_strategy": "keyword",  # keyword, all, or llm
  "top_k": 5
}
```

### Health Check
```bash
GET /health
```

### List Domains
```bash
GET /domains
```

### Clear Conversation
```bash
POST /chat/clear?conversation_id=<id>
```

## Deployment to Cloud Run

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_LOCATION="us-central1"
export FINANCE_BUCKET="finance-bucket"
export LEGAL_BUCKET="legal-bucket"
export HEALTHCARE_BUCKET="healthcare-bucket"
export FINANCE_DATASTORE_ID="finance-datastore"
export LEGAL_DATASTORE_ID="legal-datastore"
export HEALTHCARE_DATASTORE_ID="healthcare-datastore"

# Deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## Project Structure

```
google-hackathon/
├── src/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── agents/
│   │   ├── domain_agents.py       # Domain-specific search agents
│   │   └── orchestrator.py        # Query routing and aggregation
│   ├── ingestion/
│   │   ├── document_processor.py  # Multi-format text extraction
│   │   └── vertex_search.py       # Vertex AI Search integration
│   └── llm/
│       └── response_generator.py  # Gemini response generation
├── scripts/
│   ├── setup_buckets.py          # Create GCS buckets
│   ├── setup_datastores.py       # Create search datastores
│   ├── ingest_documents.py       # Ingest documents to search
│   └── deploy.sh                 # Deploy to Cloud Run
├── tests/
│   └── test_api.py               # Integration tests
├── config.yaml                    # Application configuration
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container definition
└── README.md                     # This file
```

## Usage Examples

### Single Domain Query
```python
import requests

response = requests.post("http://localhost:8080/chat", json={
    "query": "What are the financial reporting requirements?",
    "routing_strategy": "keyword"
})
print(response.json()["answer"])
```

### Multi-Turn Conversation
```python
# First message
response1 = requests.post("http://localhost:8080/chat", json={
    "query": "What are patient intake procedures?"
})
conv_id = response1.json()["conversation_id"]

# Follow-up with context
response2 = requests.post("http://localhost:8080/chat", json={
    "query": "What documents are needed for that?",
    "conversation_id": conv_id
})
```

### Cross-Domain Query
```python
response = requests.post("http://localhost:8080/chat", json={
    "query": "What are the legal and financial requirements for patient data storage?",
    "routing_strategy": "keyword"
})
# Will query both legal and finance domains
```

## Supported File Formats

- **PDF** (.pdf)
- **Word** (.docx, .doc)
- **Excel** (.xlsx, .xls)
- **CSV** (.csv)
- **HTML** (.html, .htm)
- **Text** (.txt)

## Configuration

### Chunking Parameters
- `chunk_size`: 800 tokens (configurable in config.yaml)
- `chunk_overlap`: 200 tokens
- `min_chunk_size`: 100 tokens

### LLM Parameters
- Model: `gemini-1.5-pro`
- Temperature: 0.2 (factual responses)
- Max output tokens: 2048

### Routing Strategies
- `keyword`: Route based on domain-specific keywords (default)
- `all`: Query all domains
- `llm`: Use LLM for intelligent routing (planned)

## Troubleshooting

### Authentication Errors
```bash
gcloud auth application-default login
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Datastore Not Found
Ensure datastores are created and IDs match configuration:
```bash
python scripts/setup_datastores.py --all
```

## Security Considerations

- Enable authentication for production deployments
- Use service accounts with minimal permissions
- Store sensitive configuration in Secret Manager
- Enable CORS only for trusted origins
- Implement rate limiting

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
