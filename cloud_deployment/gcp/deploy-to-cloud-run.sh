#!/bin/bash

# Google Cloud Run Deployment Script for AI Customer Service Platform
# This script deploys the application to Google Cloud Run with minimal configuration

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-ai-customer-service}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Google Cloud Run deployment for AI Customer Service Platform${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install Google Cloud CLI first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 | grep -q "."; then
    echo -e "${RED}❌ Not authenticated with Google Cloud. Run 'gcloud auth login' first.${NC}"
    exit 1
fi

# Set project if not set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ PROJECT_ID not set. Please set PROJECT_ID environment variable or run 'gcloud config set project YOUR_PROJECT_ID'${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"
echo "Using project: ${PROJECT_ID}"
echo "Using region: ${REGION}"

# Step 1: Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"

gcloud services enable cloudbuild.googleapis.com --project=${PROJECT_ID}
gcloud services enable run.googleapis.com --project=${PROJECT_ID}
gcloud services enable containerregistry.googleapis.com --project=${PROJECT_ID}

echo -e "${GREEN}✅ APIs enabled${NC}"

# Step 2: Configure Docker for GCR
echo -e "${YELLOW}🐳 Configuring Docker for Google Container Registry...${NC}"

gcloud auth configure-docker --quiet

# Step 3: Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"

# Create optimized Dockerfile for Cloud Run if it doesn't exist
if [ ! -f "Dockerfile.cloudrun" ]; then
    cat > Dockerfile.cloudrun << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Set environment variables for Cloud Run
ENV PORT=8501
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
EOF
fi

docker build -f Dockerfile.cloudrun -t ${IMAGE_NAME}:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 4: Push image to Google Container Registry
echo -e "${YELLOW}📤 Pushing image to Google Container Registry...${NC}"

docker push ${IMAGE_NAME}:latest

echo -e "${GREEN}✅ Image pushed successfully${NC}"

# Step 5: Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_NAME}:latest \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --port=8501 \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=10 \
    --timeout=300 \
    --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO,STREAMLIT_SERVER_PORT=8501,STREAMLIT_SERVER_ADDRESS=0.0.0.0" \
    --project=${PROJECT_ID}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Step 6: Get service URL
echo -e "${YELLOW}🌐 Getting service information...${NC}"

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform=managed \
    --region=${REGION} \
    --format="value(status.url)" \
    --project=${PROJECT_ID})

# Step 7: Create health check and warming request
echo -e "${YELLOW}🔍 Testing deployment...${NC}"

# Wait a moment for service to be ready
sleep 10

# Test the health endpoint
HEALTH_URL="${SERVICE_URL}/_stcore/health"
if curl -f -s "${HEALTH_URL}" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, but service might still be starting up${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}🌐 Application URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📊 Cloud Console: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/overview?project=${PROJECT_ID}${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Visit your application URL to test the deployment"
echo "2. Check Cloud Run logs for any issues:"
echo "   gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}' --limit=50 --project=${PROJECT_ID}"
echo "3. Configure custom domain if needed"
echo "4. Set up monitoring and alerts"
echo "5. Consider setting up CI/CD pipeline with Cloud Build"
echo ""

# Optional: Set up basic monitoring
read -p "Would you like to set up basic monitoring? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚙️ Setting up basic monitoring...${NC}"
    
    # Create log-based metric for errors
    gcloud logging metrics create error_rate \
        --description="Error rate for AI Customer Service" \
        --log-filter="resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME} AND severity>=ERROR" \
        --project=${PROJECT_ID} \
        || echo "Metric might already exist"
    
    echo -e "${GREEN}✅ Basic monitoring configured${NC}"
    echo "View metrics at: https://console.cloud.google.com/monitoring/metrics-explorer?project=${PROJECT_ID}"
fi

# Optional: Configure custom domain
read -p "Would you like to configure a custom domain? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your custom domain (e.g., app.yourdomain.com): " custom_domain
    if [ ! -z "$custom_domain" ]; then
        echo -e "${YELLOW}🌐 Configuring custom domain...${NC}"
        
        gcloud run domain-mappings create \
            --service=${SERVICE_NAME} \
            --domain=${custom_domain} \
            --region=${REGION} \
            --project=${PROJECT_ID}
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Custom domain configured${NC}"
            echo "Please update your DNS records to point ${custom_domain} to ghs.googlehosted.com"
        else
            echo -e "${YELLOW}⚠️ Custom domain configuration failed. You can set it up manually in the console.${NC}"
        fi
    fi
fi

# Cleanup temporary files
rm -f Dockerfile.cloudrun

echo ""
echo -e "${GREEN}✅ Deployment script completed${NC}"
echo -e "${GREEN}🚀 Your AI Customer Service Platform is now live at: ${SERVICE_URL}${NC}"