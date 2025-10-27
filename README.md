Hospital Multi-Domain Chat (POC)

Overview
- Cloud Run-hosted FastAPI service exposing /chat for multi-domain queries (nursing, pharmacy, PO).
- ADK-style orchestrator routes to domain sub-agents that use Vertex AI Search (Discovery Engine) per domain.
- Answers are grounded using retrieved chunks with source attribution; supports multi-turn conversation via session_id.
- Ingestion pipeline extracts text from PDFs, DOCX, XLSX/CSV, TXT, and HTML from GCS buckets, chunks text, and indexes into Discovery Engine data stores.

Repository Layout
- app/config.py: Domain and model configuration via environment variables.
- app/ingestion.py: Multi-format ingestion + chunking from GCS.
- app/indexing.py: Upload chunk records into Vertex AI Search data store.
- app/agents.py: VertexSearchAgent and Gemini-based grounded answer generator.
- app/orchestrator.py: Hybrid routing + aggregation and multi-turn memory.
- app/web.py: FastAPI app exposing POST /chat.
- deploy.py: Build and deploy to Cloud Run using gcloud.
- Dockerfile: Container for Cloud Run.
- requirements.txt: Python dependencies.

Prerequisites
- Python 3.11
- gcloud CLI authenticated to your Google Cloud project
- Service account or user with roles: Discovery Engine Admin, Vertex AI User, Storage Object Viewer.

Environment Variables
- GOOGLE_CLOUD_PROJECT or PROJECT_ID: Your GCP project ID.
  - Get it: gcloud config get-value project
- REGION: Cloud Run region where you will deploy/run.
  - Use a valid region string like us-central1, us-east1, europe-west1, asia-southeast1 (NOT "eu-west").
  - List Cloud Run regions: gcloud run regions list
  - Set in shell for deploy script: export REGION=us-central1
- GENAI_MODEL: Gemini model (default gemini-1.5-flash-002) — fine to keep the default.
- VERTEX_LOCATION (optional): For Vertex AI model calls if you switch to aiplatform later; Discovery Engine typically uses global.
  - Default: global
- Buckets: Provide either a single BUCKET for all domains or per-domain buckets.
  - BUCKET: GCS bucket NAME to use for all domains (no gs:// prefix)
  - Or per-domain: NURSING_BUCKET, PHARMACY_BUCKET, PO_BUCKET (aliases: FINANCE_BUCKET, LEGAL_BUCKET, HEALTHCARE_BUCKET).
  - List buckets: gsutil ls or gcloud storage buckets list --project $GOOGLE_CLOUD_PROJECT
- Retrieval:
  - TOP_K_PER_DOMAIN (default 6), MAX_SOURCES (default 6)
- Chunking:
  - CHUNK_TOKENS (default 800), CHUNK_OVERLAP (default 120)
- Tip: Start by copying .env.example to .env and edit inline following the comments.

Discovery Engine Resources (auto-provisioned)
- You no longer need to create Data Stores or Serving Configs manually.
- On startup and during indexing, the app will ensure three data stores exist under default_collection/global:
  - nursing-data-store, pharmacy-data-store, po-data-store
- It will also ensure a default_serving_config exists for each data store.
- If creation fails (e.g., insufficient permissions), the API still starts but retrieval will be empty until permissions are fixed.

Ingestion + Indexing
- Ingest and index each domain from its bucket:
  python -m app.indexing nursing --prefix "" --limit 100
  python -m app.indexing pharmacy
  python -m app.indexing po
- Ensure env vars for buckets and data stores are set.

Local Run
- Install deps: pip install -r requirements.txt
- Start API: uvicorn app.web:app --host 0.0.0.0 --port 8080
- Health check:
  curl -s http://localhost:8080/healthz
- Test chat:
  curl -X POST http://localhost:8080/chat -H "Content-Type: application/json" \
    -d '{"session_id":"u1","query":"What is the patient triage protocol?"}'

Run Locally with Docker
- Quickstart (docker compose):
  1. Copy env: cp .env.example .env and fill in values
  2. Start: docker compose up --build (first run may take a few minutes)
  3. Visit http://localhost:8080/ or curl http://localhost:8080/healthz to verify
  4. Stop: docker compose down (or Ctrl+C if running in foreground)
- Build the image:
  docker build -t hospital-chat:local .
- Create a .env file in the repo root with the required environment variables (example):
  GOOGLE_CLOUD_PROJECT=your-project-id
  REGION=us-central1
  GENAI_MODEL=gemini-1.5-flash-002
  # Buckets are NAMES only (no gs:// prefix)
  # Option A: single bucket for all domains
  #BUCKET=your-shared-bucket
  # Option B: per-domain buckets
  NURSING_BUCKET=your-nursing-bucket
  PHARMACY_BUCKET=your-pharmacy-bucket
  PO_BUCKET=your-po-bucket
  TOP_K_PER_DOMAIN=6
  MAX_SOURCES=6
  CHUNK_TOKENS=800
  CHUNK_OVERLAP=120
- Option A: Run with a service account key mounted (recommended for local):
  docker run --rm -p 8080:8080 \
    --env-file .env \
    -v $(pwd)/sa-key.json:/tmp/key.json:ro \
    -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/key.json \
    --name hospital-chat hospital-chat:local
  Notes:
  - Create a service account with Discovery Engine Search Admin, Vertex AI User, and Storage Object Viewer roles and download its JSON key as sa-key.json in the repo root.
- Option B: Run using host gcloud credentials (if available):
  docker run --rm -p 8080:8080 \
    --env-file .env \
    -v $HOME/.config/gcloud:/root/.config/gcloud:ro \
    --name hospital-chat hospital-chat:local
- Option C: Run with credentials provided via environment variables (useful in CI or if you prefer not to mount files):
  - Paste the raw JSON key into .env as GOOGLE_APPLICATION_CREDENTIALS_JSON, or base64 into GOOGLE_APPLICATION_CREDENTIALS_BASE64.
  - Then run:
    docker run --rm -p 8080:8080 \
      --env-file .env \
      --name hospital-chat hospital-chat:local
  Notes:
  - The app bootstraps ADC on startup in this precedence: GOOGLE_APPLICATION_CREDENTIALS (file path) > GOOGLE_APPLICATION_CREDENTIALS_JSON (raw JSON) > GOOGLE_APPLICATION_CREDENTIALS_BASE64.
  - Avoid committing secrets; .env is ignored by .gitignore.
- Test the API:
  curl -X POST http://localhost:8080/chat -H "Content-Type: application/json" \
    -d '{"session_id":"u1","query":"What is the patient triage protocol?"}'
- Stop the container:
  docker stop hospital-chat
- Run ingestion/indexing inside the container (override entrypoint):
  docker run --rm --env-file .env \
    -v $(pwd)/sa-key.json:/tmp/key.json:ro -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/key.json \
    hospital-chat:local python -m app.indexing po

Deploy to Cloud Run
- Build and deploy:
  export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT
  python deploy.py
- The script builds with Cloud Build and deploys to Cloud Run, passing env vars.

Use the app once it's online
- Find the service URL:
  SERVICE_NAME=${SERVICE_NAME:-hospital-chat}
  SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')
  echo "$SERVICE_URL"
- Quick checks (open in browser or curl):
  - Root:  curl -s "$SERVICE_URL/"
  - Health: curl -s "$SERVICE_URL/healthz"
  - API docs (interactive Swagger UI): open "$SERVICE_URL/docs" in your browser
- Call the /chat endpoint (unauthenticated service):
  curl -s -X POST "$SERVICE_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{"session_id":"user-1","query":"What is the patient triage protocol?"}' | jq .
- Specify domains explicitly (optional: nursing, pharmacy, po):
  curl -s -X POST "$SERVICE_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{"session_id":"user-1","query":"Show me the HIPAA consent policy","domains":["pharmacy"]}' | jq .
- Multi-turn conversations:
  - Reuse the same session_id on subsequent requests to maintain history.
  - Example:
    curl -s -X POST "$SERVICE_URL/chat" -H "Content-Type: application/json" \
      -d '{"session_id":"u1","query":"What is the patient triage protocol?","domains":["po"]}' | jq .
    curl -s -X POST "$SERVICE_URL/chat" -H "Content-Type: application/json" \
      -d '{"session_id":"u1","query":"And what about medication administration timing?"}' | jq .
- If your service is NOT public (no --allow-unauthenticated), include an Identity Token:
  TOKEN=$(gcloud auth print-identity-token)
  curl -s -H "Authorization: Bearer $TOKEN" "$SERVICE_URL/healthz"
  curl -s -X POST "$SERVICE_URL/chat" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"session_id":"u1","query":"What is the patient triage protocol?"}' | jq .
- Response format (example):
  {
    "answer": "... grounded answer ...",
    "sources": [ {"label":"Source 1","domain":"po","doc_id":"...","uri":"...","metadata":{...}}, ... ],
    "domains": ["po"],
    "retrieval": {"po": 6}
  }
- Important: Index your data first for meaningful answers. From your machine or a job with credentials:
  python -m app.indexing nursing
  python -m app.indexing pharmacy
  python -m app.indexing po
  This auto-creates data stores/serving configs (if missing) and uploads chunks from your buckets.
- Troubleshooting:
  - 401/403: Add the Authorization: Bearer $(gcloud auth print-identity-token) header.
  - 404: Ensure you are calling /, /healthz, /docs, or POST /chat exactly.
  - Empty results: Verify indexing completed and the Cloud Run service account can read your buckets.
  - Logs: gcloud logs tail --project $GOOGLE_CLOUD_PROJECT --resource="cloud_run_revision" --service=$SERVICE_NAME --region=$REGION

Notes
- For hackathon speed, LLM-based routing fallback is not implemented; rule-based routing is used with default to PO.
- Generation uses google-generativeai client; in production, consider using Vertex AI via aiplatform for service account based authentication.
- Ensure the Cloud Run service account has roles: Discovery Engine Search Admin, Vertex AI User, Storage Object Viewer.
