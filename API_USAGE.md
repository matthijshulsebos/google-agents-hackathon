# Hospital Multi-Agent RAG System - HTTP API

## Overview

The HTTP API provides RESTful access to the hospital multi-agent system with RAG (Retrieval Augmented Generation) capabilities.

## Key Features

✨ **Dual Response Format**: Every query returns both a concise summary (2-3 sentences) and a full detailed answer
🤖 **Perfect for Chatbots**: Display the summary immediately, offer "show more" for detailed version
🌐 **Multilingual**: Automatic language detection (EN, ES, FR, DE)
💬 **Conversation Context**: Follow-up questions work naturally
📚 **Document Grounding**: All answers cite source documents

## Quick Start

### 1. Start the API Server

```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
python3 api.py
```

Or using uvicorn directly:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=./sakey.json
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will start at: `http://localhost:8000`

### 2. Access Interactive Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root Endpoint

```bash
GET /
```

Returns API information and available endpoints.

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "name": "Hospital Multi-Agent RAG System",
  "version": "2.0.0",
  "description": "AI-powered hospital information retrieval",
  "endpoints": {
    "query": "POST /query - Query the hospital system",
    "multi_agent": "POST /multi-agent - Query multiple agents",
    "health": "GET /health - System health check",
    "agents": "GET /agents - List available agents",
    "docs": "GET /docs - Interactive API documentation"
  },
  "supported_languages": ["English", "Spanish", "French", "German"],
  "domains": ["Nursing", "HR", "Pharmacy"]
}
```

---

### Health Check

```bash
GET /health
```

Check system health and agent status.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-10-27T10:30:00.000Z",
  "orchestrator": "healthy",
  "agents": {
    "nursing": {
      "healthy": true,
      "agent_type": "nursing",
      "search_engine": "poc-medical-csv-data_1761595774470",
      "implementation": "RAG Pipeline"
    },
    "hr": {
      "healthy": true,
      "agent_type": "hr",
      "search_engine": "poc-medical-csv-data_1761595774470",
      "implementation": "RAG Pipeline"
    },
    "pharmacy": {
      "healthy": true,
      "agent_type": "pharmacy",
      "search_engine": "poc-medical-csv-data_1761595774470",
      "implementation": "RAG Pipeline"
    }
  }
}
```

---

### Get Agent Information

```bash
GET /agents
```

List available agents and their capabilities.

**Example:**
```bash
curl http://localhost:8000/agents
```

**Response:**
```json
{
  "available_agents": ["nursing", "hr", "pharmacy"],
  "project_id": "qwiklabs-gcp-04-488d2ba9611d",
  "location": "us-central1",
  "agents": {
    "nursing": {
      "name": "Nursing Agent",
      "languages": ["English", "Spanish"],
      "specialization": "Medical procedures, protocols, patient care"
    },
    "hr": {
      "name": "HR Agent",
      "languages": ["English", "French"],
      "specialization": "Policies, benefits, leave management"
    },
    "pharmacy": {
      "name": "Pharmacy Agent",
      "languages": ["English", "German"],
      "specialization": "Medication inventory, drug information"
    }
  }
}
```

---

### Query Endpoint (Main)

```bash
POST /query
```

Send a query to the hospital system. The orchestrator will automatically route to the appropriate agent.

**Request Body:**
```json
{
  "query": "How do I insert an IV line?",
  "user_role": "nurse",            // Optional: nurse, employee, pharmacist
  "agent_override": null,          // Optional: nursing, hr, pharmacy
  "conversation_id": null          // Optional: for multi-turn conversations
}
```

**Parameters:**
- `query` (required): The user's question
- `user_role` (optional): User role for context-aware routing
- `agent_override` (optional): Force a specific agent
- `conversation_id` (optional): Continue existing conversation

#### Example 1: Nursing Query (English)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What about blood glucose monitoring?",
    "user_role": "nurse"
  }'
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What about blood glucose monitoring?",
  "answer": "Blood glucose monitoring is a critical procedure...\n\nEquipment Needed:\n1. Glucometer...",
  "answer_summary": "Blood glucose monitoring measures current blood sugar levels using a glucometer, test strip, and lancet. The procedure emphasizes hand hygiene, sterile equipment, proper sharps disposal, and documentation for patient safety.",
  "answer_detailed": "Here is information regarding blood glucose monitoring:\n\n**Overview**\nBlood glucose monitoring is a procedure used to measure the current blood glucose level...\n\n**Equipment Needed**\n* Glucometer\n* Test strip\n* Lancet\n* Gauze\n\n**Procedure Steps**\n1. Verify the order...\n2. Gather equipment...\n[Full detailed answer with all steps]",
  "agent": "nursing",
  "language": "en",
  "total_results": 34,
  "sources_count": 5,
  "grounding_metadata": [
    {
      "title": "Blood Glucose Monitoring Protocol",
      "uri": "gs://...",
      "score": 0.95
    }
  ],
  "routing_info": {
    "method": "user_role",
    "category": "nursing",
    "confidence": "high"
  },
  "timestamp": "2025-10-27T10:30:00.000Z"
}
```

**Response Fields:**
- `answer` - Full detailed answer (backward compatibility)
- `answer_summary` - **Concise 2-3 sentence summary** (for chatbot quick display)
- `answer_detailed` - Full detailed answer with all information (for "show more" functionality)

#### Example 2: HR Query (French)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Combien de jours de vacances ai-je?",
    "user_role": "employee"
  }'
```

#### Example 3: Pharmacy Query (German)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Ist Ibuprofen 400mg auf Lager?",
    "agent_override": "pharmacy"
  }'
```

#### Example 4: Multi-turn Conversation

```bash
# First query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the leave policy?"
  }'

# Response will include conversation_id: "abc-123"

# Follow-up query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many days can I carry over?",
    "conversation_id": "abc-123"
  }'
```

---

### Multi-Agent Query

```bash
POST /multi-agent
```

Query multiple agents simultaneously and compare results.

**Request Body:**
```json
{
  "query": "What are the medication protocols?",
  "agents": ["nursing", "pharmacy"]  // Optional: defaults to all agents
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/multi-agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are safety protocols?",
    "agents": ["nursing", "hr", "pharmacy"]
  }'
```

**Response:**
```json
{
  "query": "What are safety protocols?",
  "timestamp": "2025-10-27T10:30:00.000Z",
  "results": {
    "nursing": {
      "answer": "Nursing safety protocols include...",
      "agent": "nursing",
      "total_results": 28,
      "grounding_metadata": [...]
    },
    "hr": {
      "answer": "Workplace safety policies state...",
      "agent": "hr",
      "total_results": 15,
      "grounding_metadata": [...]
    },
    "pharmacy": {
      "answer": "Medication safety protocols require...",
      "agent": "pharmacy",
      "total_results": 42,
      "grounding_metadata": [...]
    }
  }
}
```

---

### Conversation Management

#### Get Conversation History

```bash
GET /conversation/{conversation_id}
```

**Example:**
```bash
curl http://localhost:8000/conversation/abc-123
```

**Response:**
```json
{
  "conversation_id": "abc-123",
  "messages": [
    {
      "timestamp": "2025-10-27T10:30:00.000Z",
      "query": "What is the leave policy?",
      "answer": "Our leave policy provides...",
      "agent": "hr"
    },
    {
      "timestamp": "2025-10-27T10:31:00.000Z",
      "query": "How many days can I carry over?",
      "answer": "You can carry over up to...",
      "agent": "hr"
    }
  ],
  "message_count": 2
}
```

#### Clear Conversation

```bash
DELETE /conversation/{conversation_id}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/conversation/abc-123
```

---

## Language Support

The system automatically detects the query language:

- **English**: Default for all agents
- **Spanish**: Nursing agent (`¿Cómo insertar una vía intravenosa?`)
- **French**: HR agent (`Combien de jours de vacances?`)
- **German**: Pharmacy agent (`Ist Ibuprofen verfügbar?`)

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service not initialized

**Error Response Format:**
```json
{
  "detail": "Error description",
  "error": "Detailed error message"
}
```

## Python Client Example

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000"

def query_hospital_system(query, user_role=None):
    """Query the hospital system."""
    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "query": query,
            "user_role": user_role
        }
    )
    return response.json()

# Example usage
result = query_hospital_system(
    "How do I insert an IV line?",
    user_role="nurse"
)

# Display summary for quick view
print(f"Summary: {result['answer_summary']}")
print(f"Agent: {result['agent']}")
print(f"Sources: {result['sources_count']}")

# User can request detailed view
if user_wants_details:
    print(f"\nDetailed Answer:\n{result['answer_detailed']}")
```

## JavaScript/TypeScript Client Example

```typescript
const BASE_URL = 'http://localhost:8000';

async function queryHospitalSystem(query: string, userRole?: string) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      user_role: userRole,
    }),
  });

  return await response.json();
}

// Example usage
const result = await queryHospitalSystem(
  'What are the public holidays?',
  'employee'
);

console.log('Answer:', result.answer);
console.log('Agent:', result.agent);
console.log('Language:', result.language);
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Simple query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What about blood glucose monitoring?"}'

# With user role
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many vacation days?", "user_role": "employee"}'
```

### Using HTTPie

```bash
# Health check
http GET localhost:8000/health

# Query
http POST localhost:8000/query \
  query="What about blood glucose monitoring?" \
  user_role="nurse"
```

### Using Python requests

```python
import requests

# Health check
health = requests.get("http://localhost:8000/health").json()
print(health)

# Query
response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What about blood glucose monitoring?"}
)
print(response.json())
```

## Production Considerations

For production deployment:

1. **Environment Variables**: Set proper configuration
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   export GCP_PROJECT_ID=your-project-id
   ```

2. **CORS**: Update CORS settings in `api.py` to restrict origins
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Authentication**: Add authentication middleware (JWT, API keys, etc.)

4. **Rate Limiting**: Implement rate limiting to prevent abuse

5. **Logging**: Configure production logging (e.g., to Google Cloud Logging)

6. **Deployment**: Use production ASGI server
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## Architecture

The API uses:
- **FastAPI**: Modern async web framework
- **HospitalOrchestrator**: Intelligent query routing
- **RAG Pipeline**: Vertex AI Search + Gemini 2.5 Flash
- **Three Specialized Agents**: Nursing, HR, Pharmacy

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   FastAPI   │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Orchestrator    │
│  (Routing Logic) │
└──────┬───────────┘
       │
    ┌──┴───┬────────┐
    │      │        │
    ▼      ▼        ▼
┌────────┬────────┬─────────┐
│Nursing │  HR    │Pharmacy │
│ Agent  │ Agent  │ Agent   │
└───┬────┴───┬────┴────┬────┘
    │        │         │
    └────┬───┴─────┬───┘
         │         │
         ▼         ▼
    ┌─────────────────────┐
    │   RAG Pipeline      │
    ├─────────────────────┤
    │ Vertex AI Search    │
    │ Gemini 2.5 Flash    │
    └─────────────────────┘
```

## Chatbot Integration Example

The dual response format is perfect for chatbot UIs:

### React Chatbot Component

```jsx
function ChatMessage({ message }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="chat-message">
      {/* Always show summary first */}
      <p className="summary">{message.answer_summary}</p>

      {/* Show more button */}
      {!showDetails && (
        <button onClick={() => setShowDetails(true)}>
          Show detailed answer
        </button>
      )}

      {/* Detailed view (on demand) */}
      {showDetails && (
        <div className="detailed-answer">
          <p>{message.answer_detailed}</p>
          <div className="sources">
            <small>{message.sources_count} sources cited</small>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div class="chat-message">
    <!-- Summary (always visible) -->
    <p class="summary">{{ message.answer_summary }}</p>

    <!-- Toggle button -->
    <button v-if="!showDetails" @click="showDetails = true">
      Show more
    </button>

    <!-- Detailed answer (expandable) -->
    <div v-if="showDetails" class="details">
      <p>{{ message.answer_detailed }}</p>
      <small>{{ message.sources_count }} sources</small>
    </div>
  </div>
</template>

<script>
export default {
  props: ['message'],
  data() {
    return { showDetails: false };
  }
};
</script>
```

### Benefits for Chatbots

✅ **Fast Initial Response**: Show summary immediately
✅ **Clean UI**: No overwhelming walls of text
✅ **User Control**: Let users decide if they want details
✅ **Better UX**: Progressive disclosure pattern
✅ **Mobile Friendly**: Concise summaries work better on small screens

## Support

For issues or questions:
- Check logs: API logs all requests and errors
- Interactive docs: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health
