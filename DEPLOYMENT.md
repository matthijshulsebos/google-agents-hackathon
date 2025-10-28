# 🚀 Deployment Guide - Hospital AI Assistant

## Quick Start Options

### Option 1: Terminal Chat (Immediate Testing) ⚡

**Simplest way to test your assistant:**

```bash
python interactive_chat.py
```

- ✅ No installation needed (uses existing environment)
- ✅ Maintains conversation context
- ✅ Perfect for quick testing and demos

**Example:**
```
👤 You: How do I insert a peripheral IV?
🤖 Assistant: To insert a peripheral IV (PIV), follow these steps...
```

---

### Option 2: Streamlit Web App (Best for Demos) 🌐

**Beautiful, interactive web interface:**

1. **Install Streamlit:**
```bash
pip install streamlit
```

2. **Run the app:**
```bash
streamlit run app.py
```

3. **Open browser:** App automatically opens at `http://localhost:8501`

**Features:**
- ✨ Modern chat interface
- 💬 Conversation history
- 📚 Source citations
- 🎨 Clean, professional UI
- 📱 Responsive design

**Best for:**
- Internal team demos
- Stakeholder presentations
- User testing sessions

---

### Option 3: Flask REST API (For Integration) 🔌

**RESTful API for integrating with other systems:**

1. **Install Flask:**
```bash
pip install flask flask-cors
```

2. **Run the API:**
```bash
python api.py
```

3. **API is available at:** `http://localhost:5000`

**Endpoints:**

- `POST /api/chat` - Send a message
  ```json
  {
    "message": "What is the procedure for IV insertion?",
    "session_id": "user-123"
  }
  ```

- `GET /api/domains` - List available knowledge domains
- `POST /api/clear-session` - Clear conversation history
- `GET /health` - Health check

**Best for:**
- Integrating with existing hospital systems
- Mobile app backends
- Custom frontends

---

## Cloud Deployment Options

### Option A: Google Cloud Run (Recommended) ☁️

**Fully managed, serverless container deployment:**

1. **Create Dockerfile** (already exists in your project)

2. **Build and deploy:**
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/hospital-assistant

# Deploy to Cloud Run
gcloud run deploy hospital-assistant \
  --image gcr.io/PROJECT_ID/hospital-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=PROJECT_ID,GCP_LOCATION=eu
```

3. **Access your app:** Cloud Run provides a URL like `https://hospital-assistant-xxx.run.app`

**Cost:** Pay only when requests are being processed (~$0.40/million requests)

---

### Option B: Google App Engine

**Simple platform-as-a-service:**

1. **Create `app.yaml`:**
```yaml
runtime: python312
entrypoint: streamlit run app.py --server.port=$PORT

env_variables:
  GCP_PROJECT_ID: "your-project-id"
  GCP_LOCATION: "eu"
```

2. **Deploy:**
```bash
gcloud app deploy
```

---

### Option C: Vertex AI Endpoints (Enterprise)

**For high-traffic, production use:**

Deploy as a custom prediction endpoint with:
- Auto-scaling
- Load balancing
- Built-in monitoring
- VPC integration

---

## Production Recommendations

### Security
- [ ] Enable authentication (OAuth 2.0, IAM)
- [ ] Use Secret Manager for API keys
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Enable audit logging

### Performance
- [ ] Add Redis for session management
- [ ] Implement response caching
- [ ] Use Cloud CDN for static assets
- [ ] Enable request queuing

### Monitoring
- [ ] Set up Cloud Monitoring dashboards
- [ ] Configure alerts for errors/latency
- [ ] Track usage metrics per domain
- [ ] Monitor Gemini API quota

### Sample Production Stack

```
┌─────────────────────────────────────────┐
│  Cloud Load Balancer (HTTPS)            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Cloud Run (Streamlit/Flask)            │
│  - Auto-scaling (0-100 instances)       │
│  - Health checks                         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Vertex AI Search (3 datastores)        │
│  - nursing-datastore-v6                 │
│  - pharmacy-datastore-v6                │
│  - po-datastore-v6                      │
└─────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  Gemini 2.0 Flash (Agent/LLM)          │
└─────────────────────────────────────────┘
```

---

## Testing Your Deployment

### 1. Quick Test (Terminal)
```bash
python interactive_chat.py
```

### 2. Test API
```bash
# Start API
python api.py

# In another terminal
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about blood glucose monitoring"}'
```

### 3. Load Test (Optional)
```bash
# Install hey
go install github.com/rakyll/hey@latest

# Run load test
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' \
  http://localhost:5000/api/chat
```

---

## Cost Estimates (Monthly)

**Development/Testing:**
- Vertex AI Search: ~$0 (free tier)
- Gemini API: ~$10-50 (depends on usage)
- Cloud Run: ~$0 (generous free tier)
- **Total: ~$10-50/month**

**Production (1000 users, 10k queries/month):**
- Vertex AI Search: ~$100
- Gemini API: ~$200-500
- Cloud Run: ~$50
- Load Balancer: ~$20
- **Total: ~$370-670/month**

---

## Next Steps

1. **Test locally first:**
   ```bash
   python interactive_chat.py
   ```

2. **Try the web interface:**
   ```bash
   pip install streamlit
   streamlit run app.py
   ```

3. **When ready for production:**
   - Review security checklist
   - Set up monitoring
   - Deploy to Cloud Run
   - Configure custom domain

---

## Need Help?

- 📖 [Streamlit Docs](https://docs.streamlit.io/)
- 📖 [Cloud Run Docs](https://cloud.google.com/run/docs)
- 📖 [Vertex AI Search Docs](https://cloud.google.com/vertex-ai-search-and-conversation/docs)
- 📖 [Gemini API Docs](https://ai.google.dev/docs)
