#!/bin/bash
# DatasetDoctor - Cloud Run Deployment Script

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 DatasetDoctor - Cloud Run Deployment${NC}"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${YELLOW}⚠️  gcloud CLI not found. Please install Google Cloud SDK${NC}"
    echo "   Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud${NC}"
    echo "   Running: gcloud auth login"
    gcloud auth login
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️  No project ID set${NC}"
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}✅ Project ID: ${PROJECT_ID}${NC}"

# Enable required APIs
echo -e "\n${BLUE}Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo -e "\n${BLUE}Building and deploying to Cloud Run...${NC}"
gcloud builds submit --config=deployment/cloud-run/cloudbuild.yaml

# Get service URL
SERVICE_URL=$(gcloud run services describe datasetdoctor --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "\n${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
    echo -e "\n${BLUE}To view logs:${NC}"
    echo "   gcloud run services logs read datasetdoctor --region=us-central1"
    echo -e "\n${BLUE}To update environment variables:${NC}"
    echo "   gcloud run services update datasetdoctor --region=us-central1 --set-env-vars GOOGLE_API_KEY=your_key"
else
    echo -e "\n${YELLOW}⚠️  Deployment completed. Check Cloud Run console for service URL.${NC}"
fi

echo -e "\n${GREEN}✨ Done!${NC}"

