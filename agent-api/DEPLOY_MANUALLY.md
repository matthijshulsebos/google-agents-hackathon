# Manual Deployment Guide for hospital-agent-api

## Current Status

✅ **Container built successfully!**

Image: `gcr.io/qwiklabs-gcp-04-488d2ba9611d/hospital-agent-api:latest`

The Docker container has been built and pushed to Google Container Registry. You just need to deploy it to Cloud Run.

## Option 1: Deploy via Google Cloud Console (Recommended)

Since there's a local gcloud CLI issue, the easiest way is to use the Cloud Console:

### Steps:

1. **Go to Cloud Run**
   - Open https://console.cloud.google.com/run?project=qwiklabs-gcp-04-488d2ba9611d
   - Click "CREATE SERVICE"

2. **Configure the service**
   - Select: **Deploy one revision from an existing container image**
   - Container image URL: `gcr.io/qwiklabs-gcp-04-488d2ba9611d/hospital-agent-api:latest`
   - Click "SELECT"

3. **Service settings**
   - Service name: `hospital-agent-api`
   - Region: `us-central1 (Iowa)`
   - Authentication: **Allow unauthenticated invocations** (check the box)

4. **Container, Networking, Security**
   Click "CONTAINER, VARIABLES & SECRETS, CONNECTIONS, SECURITY"

   **Container tab:**
   - Container port: `8080`
   - Memory: `2 GiB`
   - CPU: `2`
   - Request timeout: `300` seconds
   - Maximum requests per container: `80`

   **Variables & Secrets tab:**
   Add these environment variables (click "ADD VARIABLE" for each):
   ```
   GCP_PROJECT_ID = qwiklabs-gcp-04-488d2ba9611d
   GCP_LOCATION = us-central1
   NURSING_DATASTORE_ID = poc-medical-csv-data_1761595774470
   HR_DATASTORE_ID = poc-medical-csv-data_1761595774470
   PHARMACY_DATASTORE_ID = poc-medical-csv-data_1761595774470
   MODEL_NAME = gemini-2.5-flash
   TEMPERATURE = 0.2
   DYNAMIC_THRESHOLD = 0.3
   MAX_RESULTS = 5
   LOG_LEVEL = INFO
   TIMEOUT = 30
   ENVIRONMENT = production
   ```

   **Security tab:**
   - Service account: `hospital-chat-sa@qwiklabs-gcp-04-488d2ba9611d.iam.gserviceaccount.com`

5. **Autoscaling**
   - Minimum number of instances: `0`
   - Maximum number of instances: `10`

6. **Click CREATE**

7. **Wait for deployment** (usually takes 1-2 minutes)

8. **Get the URL** - You'll see a URL like: `https://hospital-agent-api-XXXXX-uc.a.run.app`

## Option 2: Fix gcloud and run deploy.sh

If you want to fix the gcloud issue first:

```bash
# Reinstall gcloud components
gcloud components reinstall

# Or update gcloud
gcloud components update

# Then run
cd agent-api
./deploy.sh
```

## Option 3: Use the service.yaml file

If you can fix gcloud, you can use the service.yaml file:

```bash
gcloud run services replace service.yaml \
  --region=us-central1 \
  --project=qwiklabs-gcp-04-488d2ba9611d \
  --platform=managed
```

Then set public access:
```bash
gcloud run services add-iam-policy-binding hospital-agent-api \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=qwiklabs-gcp-04-488d2ba9611d
```

## After Deployment

Test your API:

```bash
# Replace <SERVICE_URL> with your actual Cloud Run URL
SERVICE_URL="https://hospital-agent-api-XXXXX-uc.a.run.app"

# Health check
curl $SERVICE_URL/health

# API docs (open in browser)
open $SERVICE_URL/docs

# Test query
curl -X POST $SERVICE_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I insert an IV?"}'

# Test research endpoint
curl -X POST $SERVICE_URL/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What do I need to do today with patient Juan de Marco?"}'
```

## View Logs

```bash
gcloud run services logs read hospital-agent-api \
  --region us-central1 \
  --project qwiklabs-gcp-04-488d2ba9611d
```

Or via Cloud Console:
https://console.cloud.google.com/run/detail/us-central1/hospital-agent-api/logs?project=qwiklabs-gcp-04-488d2ba9611d
