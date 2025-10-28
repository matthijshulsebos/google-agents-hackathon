#!/bin/bash
# Deploy the application to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_LOCATION:-us-central1}"
SERVICE_NAME="hospital-chat-service"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if project ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

echo "=== Deploying Hospital Chat System to Cloud Run ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Build the Docker image
echo "Building Docker image..."
docker build -t "${IMAGE_NAME}:latest" .

# Configure Docker to use gcloud as credential helper
echo "Configuring Docker authentication..."
gcloud auth configure-docker

# Push the image to Google Container Registry
echo "Pushing image to GCR..."
docker push "${IMAGE_NAME}:latest"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE_NAME}:latest" \
    --platform=managed \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION}" \
    --set-env-vars="NURSING_BUCKET=${NURSING_BUCKET},PHARMACY_BUCKET=${PHARMACY_BUCKET},PO_BUCKET=${PO_BUCKET}" \
    --set-env-vars="NURSING_DATASTORE_ID=${NURSING_DATASTORE_ID},PHARMACY_DATASTORE_ID=${PHARMACY_DATASTORE_ID},PO_DATASTORE_ID=${PO_DATASTORE_ID}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --platform=managed \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --format="value(status.url)")

echo ""
echo "=== Deployment Complete! ==="
echo "Service URL: ${SERVICE_URL}"
echo "Health Check: ${SERVICE_URL}/health"
echo "API Docs: ${SERVICE_URL}/docs"
echo ""
