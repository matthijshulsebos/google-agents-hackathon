# Hospital Multi-Agent Information Retrieval System

A sophisticated AI-powered hospital information system that intelligently assists nurses, HR staff, and pharmacists with domain-specific queries using Google's Vertex AI and multi-agent orchestration.

## 🚀 Live Demo

**Application URL**: https://qwiklabs-gcp-04-488d2ba9611d.web.app

**API Endpoint**: https://hospital-agent-api-732642765257.us-central1.run.app

## 💡 Value Proposition

- **Intelligent Information Retrieval**: Get instant answers to domain-specific questions with AI-powered document search and grounding
- **Multi-Agent Orchestration**: Automatically routes queries to specialized agents (Nursing, HR, Pharmacy) for accurate, domain-specific responses
- **Multilingual Support**: Interact in English, Spanish, French, or German with automatic language detection
- **Real-Time Medication Tracking**: Check medication inventory, batch information, storage requirements, and controlled substance status
- **Contextual Conversations**: Maintains conversation history for follow-up questions and deeper exploration
- **Document-Grounded Responses**: All answers are backed by verified hospital documents with proper citations

## 🎯 Try These Sample Queries

### Nursing (English/Spanish)
- "How do I insert an IV line?"
- "What is the protocol for wound dressing?"
- "¿Cuál es el protocolo para administrar medicamentos?" (Spanish)

### HR (English/French)
- "How many vacation days do I have?"
- "What are the public holidays this year?"
- "Combien de jours de congé ai-je?" (French)

### Pharmacy (English/German)
- "Is ibuprofen 400mg in stock?"
- "Show me the inventory for acetaminophen"
- "Ist Paracetamol verfügbar?" (German)

### General Queries (Auto-routed)
- "What's the procedure for medication administration?"
- "When can I request time off?"
- "Do we have any antibiotics in stock?"

## 🏗️ Technology Stack

### Frontend (agent-ui)
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Icon library
- **React Markdown** - Rich message rendering
- **Firebase Hosting** - Scalable web hosting

### Backend (agent-api)
- **Python 3.11** - Modern Python runtime
- **FastAPI** - High-performance async web framework
- **Google ADK (Application Development Kit)** - AI agent framework
- **Vertex AI Search** - Document retrieval and grounding
- **Gemini 2.0 Flash** - Advanced language model
- **Cloud Run** - Serverless container deployment

### Infrastructure
- **Google Cloud Platform** - Cloud infrastructure
- **Vertex AI** - AI/ML platform
- **Cloud Storage** - Document storage
- **Cloud Run** - Serverless compute
- **Firebase** - Frontend hosting

## 📁 Project Structure

```
google-agents-hackathon/
├── agent-api/                 # Backend API service
│   ├── agents/                # Specialized AI agents
│   │   ├── nursing_agent.py   # Medical procedures agent
│   │   ├── hr_agent.py        # HR policies agent
│   │   └── pharmacy_agent.py  # Medication inventory agent
│   ├── orchestrator.py        # Query routing orchestrator
│   ├── api.py                 # FastAPI application
│   └── Dockerfile             # Container configuration
│
└── agent-ui/                  # Frontend React application
    ├── src/
    │   ├── components/        # React components
    │   ├── services/          # API integration
    │   └── context/           # State management
    └── firebase.json          # Firebase configuration
```

## 🎨 Features

### Multi-Agent Orchestration
- **Intelligent Routing**: Automatically determines which specialized agent should handle each query
- **Domain Expertise**: Each agent is optimized for its specific domain (Nursing, HR, Pharmacy)
- **Keyword & AI Classification**: Uses both keyword matching and AI-powered classification

### Multilingual Support
- **4 Languages**: English, Spanish, French, German
- **Auto-Detection**: Automatically detects query language
- **Native Responses**: Responds in the same language as the query

### Document Grounding
- **Vertex AI Search**: Powered by Google's enterprise search technology
- **Citation Tracking**: All answers include references to source documents
- **Verified Information**: Responses based on actual hospital policies and protocols

### Interactive UI
- **Chat Interface**: Conversational interface for natural queries
- **Medication Panels**: Rich display of medication inventory data
- **Alert System**: Real-time critical and warning alerts
- **Quick Actions**: Fast access to common queries
- **Responsive Design**: Works on desktop and mobile devices

## 🚦 How It Works

1. **User Query**: User submits a question through the web interface
2. **Language Detection**: System detects the query language
3. **Intelligent Routing**: Orchestrator routes to appropriate agent (Nursing/HR/Pharmacy)
4. **Document Search**: Agent queries Vertex AI Search for relevant documents
5. **AI Response**: Gemini 2.0 generates grounded response with citations
6. **Rich Display**: UI renders response with formatting, citations, and structured data

## 📊 Architecture Overview

```
┌─────────────┐
│   User UI   │ (React + Firebase)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ (Cloud Run)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Orchestrator│ (Query Classification)
└──────┬──────┘
       │
       ├──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼
   Nursing     HR Agent   Pharmacy  (Specialized)
   Agent                   Agent
       │          │          │
       ▼          ▼          ▼
┌────────────────────────────────┐
│    Vertex AI Search            │
│  (3 Domain-Specific Stores)    │
└────────────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  Hospital Documents (PDF/MD)   │
└────────────────────────────────┘
```

## 🛠️ Development

### Backend Setup
```bash
cd agent-api
pip install -r requirements.txt
uvicorn api:app --reload
```

### Frontend Setup
```bash
cd agent-ui
npm install
npm run dev
```

### Deployment
- **Frontend**: Deployed to Firebase Hosting
- **Backend**: Deployed to Google Cloud Run

## 📝 Documentation

- [Agent API Documentation](./agent-api/README.md) - Backend API details
- [Agent UI Documentation](./agent-ui/README.md) - Frontend application guide
- [Google Agents Integration](./agent-ui/GOOGLE_AGENTS_INTEGRATION.md) - API integration guide

## 🏆 Built For

Google ADK Hackathon - Multi-Agent Information Retrieval System

## 📄 License

MIT License
