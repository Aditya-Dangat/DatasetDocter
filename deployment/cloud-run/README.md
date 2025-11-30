# Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed (`gcloud` CLI)
3. **Docker** (for local testing)

## Quick Deploy

```bash
# Make deploy script executable
chmod +x deployment/cloud-run/deploy.sh

# Run deployment
./deployment/cloud-run/deploy.sh
```

## Manual Deployment Steps

### 1. Set Up Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Build Docker Image

```bash
# Build locally (for testing)
docker build -t datasetdoctor:latest .

# Test locally
docker run -p 8080:8080 -e GOOGLE_API_KEY=your_key datasetdoctor:latest
```

### 3. Deploy to Cloud Run

**Option A: Using Cloud Build (Recommended)**
```bash
gcloud builds submit --config=deployment/cloud-run/cloudbuild.yaml
```

**Option B: Manual Deployment**
```bash
# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/datasetdoctor

# Deploy to Cloud Run
gcloud run deploy datasetdoctor \
  --image gcr.io/YOUR_PROJECT_ID/datasetdoctor \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "PORT=8080,FLASK_ENV=production"
```

### 4. Set Environment Variables

```bash
gcloud run services update datasetdoctor \
  --region us-central1 \
  --set-env-vars "GOOGLE_API_KEY=your_api_key_here"
```

## Health Check

The Dockerfile includes a health check endpoint. Add this to your Flask app:

```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

## Configuration

### Environment Variables

- `PORT`: Server port (default: 8080)
- `FLASK_ENV`: Environment (production/development)
- `GOOGLE_API_KEY`: Gemini API key (optional)
- `PROJECT_ID`: Google Cloud Project ID (for Vertex AI)
- `REGION`: Google Cloud region (default: us-central1)

### Resource Limits

- **Memory**: 2GB (adjustable)
- **CPU**: 2 vCPU (adjustable)
- **Timeout**: 300 seconds (5 minutes)
- **Max Instances**: 10 (auto-scales)

## Monitoring

```bash
# View logs
gcloud run services logs read datasetdoctor --region=us-central1

# View service details
gcloud run services describe datasetdoctor --region=us-central1

# View metrics
gcloud run services describe datasetdoctor --region=us-central1 --format="value(status.url)"
```

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check Cloud Build logs: `gcloud builds list`

### Deployment Fails
- Verify project ID is correct
- Check API permissions
- Ensure billing is enabled

### Service Not Accessible
- Check if service allows unauthenticated access
- Verify firewall rules
- Check service logs for errors

## Cost Estimation

Cloud Run pricing (approximate):
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

For light usage: ~$5-10/month
For moderate usage: ~$20-50/month

## Security Notes

1. **API Keys**: Store in Cloud Run secrets, not in code
2. **Authentication**: Consider requiring authentication for production
3. **HTTPS**: Cloud Run provides HTTPS by default
4. **File Storage**: Use Cloud Storage for persistent file storage

## Next Steps

1. Set up Cloud Storage for file persistence
2. Configure custom domain
3. Set up monitoring and alerts
4. Configure CI/CD pipeline

