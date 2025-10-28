#!/bin/bash
set -e

# Hospital Agent API - Cloud Run Deployment Script
# This script builds and deploys the agent-api to Google Cloud Run

echo "=========================================="
echo "Hospital Agent API - Cloud Run Deployment"
echo "=========================================="

# Configuration
PROJECT_ID="qwiklabs-gcp-04-488d2ba9611d"
SERVICE_NAME="hospital-agent-api"
REGION="us-central1"
SERVICE_ACCOUNT="hospital-chat-sa@qwiklabs-gcp-04-488d2ba9611d.iam.gserviceaccount.com"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Set the project
echo ""
echo "Setting GCP project to: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Load environment variables from .env
echo ""
echo "Loading environment variables from .env file..."
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with required configuration."
    exit 1
fi

# Extract environment variables (excluding GOOGLE_APPLICATION_CREDENTIALS)
ENV_VARS=$(grep -v '^#' .env | grep -v '^$' | grep -v 'GOOGLE_APPLICATION_CREDENTIALS' | sed 's/^/--set-env-vars /' | tr '\n' ' ')

echo "Environment variables loaded:"
grep -v '^#' .env | grep -v '^$' | grep -v 'GOOGLE_APPLICATION_CREDENTIALS' | cut -d'=' -f1 | sed 's/^/  - /'

# Build container with Cloud Build
echo ""
echo "Building container image with Cloud Build..."
echo "Image: ${IMAGE_NAME}"
gcloud builds submit --tag ${IMAGE_NAME} .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Container build failed!"
    exit 1
fi

echo ""
echo "Container built successfully!"

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"

gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --service-account ${SERVICE_ACCOUNT} \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 8 \
    --min-instances 0 \
    ${ENV_VARS}

# Check if deployment was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Cloud Run deployment failed!"
    exit 1
fi

# Get the service URL
echo ""
echo "=========================================="
echo "Deployment successful!"
echo "=========================================="
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Test the API:"
echo "  Health check: curl ${SERVICE_URL}/health"
echo "  API docs:     ${SERVICE_URL}/docs"
echo "  Query API:    curl -X POST ${SERVICE_URL}/query -H 'Content-Type: application/json' -d '{\"query\":\"How do I insert an IV?\"}'"
echo ""
echo "To view logs:"
echo "  gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
echo ""
echo "=========================================="
