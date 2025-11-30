# Local Docker Deployment

## Quick Start

```bash
# Build and run with Docker Compose
cd deployment/local
docker-compose up --build

# Access at: http://localhost:8080
```

## Manual Docker Commands

```bash
# Build image
docker build -t datasetdoctor:latest ..

# Run container
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=your_key \
  -v $(pwd)/../../uploads:/app/uploads \
  -v $(pwd)/../../outputs:/app/outputs \
  datasetdoctor:latest

# Run in background
docker run -d -p 8080:8080 --name datasetdoctor datasetdoctor:latest

# View logs
docker logs -f datasetdoctor

# Stop container
docker stop datasetdoctor
docker rm datasetdoctor
```

## Environment Variables

Create a `.env` file or set environment variables:

```bash
GOOGLE_API_KEY=your_api_key
PROJECT_ID=your_project_id
REGION=us-central1
PORT=8080
FLASK_ENV=development
```

## Testing

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test file upload (requires file)
curl -X POST -F "file=@sample.csv" http://localhost:8080/upload
```

