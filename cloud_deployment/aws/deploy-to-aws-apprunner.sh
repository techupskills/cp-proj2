#!/bin/bash

# AWS App Runner Deployment Script for AI Customer Service Platform
# This script deploys the application to AWS App Runner with minimal configuration

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_NAME="ai-customer-service"
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}"
SERVICE_NAME="ai-customer-service-app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AWS App Runner deployment for AI Customer Service Platform${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Step 1: Create ECR repository if it doesn't exist
echo -e "${YELLOW}📦 Setting up ECR repository...${NC}"

if ! aws ecr describe-repositories --repository-names ${IMAGE_NAME} --region ${AWS_REGION} &> /dev/null; then
    echo "Creating ECR repository: ${IMAGE_NAME}"
    aws ecr create-repository \
        --repository-name ${IMAGE_NAME} \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    echo -e "${GREEN}✅ ECR repository created${NC}"
else
    echo -e "${GREEN}✅ ECR repository already exists${NC}"
fi

# Step 2: Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"

docker build -t ${IMAGE_NAME}:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 3: Login to ECR and push image
echo -e "${YELLOW}📤 Pushing image to ECR...${NC}"

# Get ECR login token
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY%/*}

# Tag and push image
docker tag ${IMAGE_NAME}:latest ${ECR_REPOSITORY}:latest
docker push ${ECR_REPOSITORY}:latest

echo -e "${GREEN}✅ Image pushed to ECR successfully${NC}"

# Step 4: Create App Runner service configuration
echo -e "${YELLOW}⚙️ Creating App Runner service configuration...${NC}"

cat > apprunner-service.json << EOF
{
  "ServiceName": "${SERVICE_NAME}",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "${ECR_REPOSITORY}:latest",
      "ImageConfiguration": {
        "Port": "8501",
        "RuntimeEnvironmentVariables": {
          "ENVIRONMENT": "production",
          "LOG_LEVEL": "INFO",
          "STREAMLIT_SERVER_PORT": "8501",
          "STREAMLIT_SERVER_ADDRESS": "0.0.0.0"
        },
        "StartCommand": "streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  },
  "HealthCheckConfiguration": {
    "Protocol": "HTTP",
    "Path": "/_stcore/health",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  }
}
EOF

# Step 5: Create or update App Runner service
echo -e "${YELLOW}🚀 Deploying to App Runner...${NC}"

# Check if service already exists
if aws apprunner describe-service --service-arn "arn:aws:apprunner:${AWS_REGION}:${AWS_ACCOUNT_ID}:service/${SERVICE_NAME}" &> /dev/null; then
    echo "Service exists, updating..."
    aws apprunner update-service \
        --service-arn "arn:aws:apprunner:${AWS_REGION}:${AWS_ACCOUNT_ID}:service/${SERVICE_NAME}" \
        --source-configuration file://apprunner-service.json
else
    echo "Creating new App Runner service..."
    aws apprunner create-service --cli-input-json file://apprunner-service.json
fi

# Step 6: Wait for deployment and get URL
echo -e "${YELLOW}⏳ Waiting for service to be ready...${NC}"

SERVICE_ARN="arn:aws:apprunner:${AWS_REGION}:${AWS_ACCOUNT_ID}:service/${SERVICE_NAME}"

# Wait for service to be running
while true; do
    STATUS=$(aws apprunner describe-service --service-arn ${SERVICE_ARN} --query 'Service.Status' --output text)
    
    if [ "$STATUS" = "RUNNING" ]; then
        break
    elif [ "$STATUS" = "CREATE_FAILED" ] || [ "$STATUS" = "UPDATE_FAILED" ]; then
        echo -e "${RED}❌ Service deployment failed. Status: ${STATUS}${NC}"
        exit 1
    else
        echo "Current status: ${STATUS}. Waiting..."
        sleep 30
    fi
done

# Get service URL
SERVICE_URL=$(aws apprunner describe-service --service-arn ${SERVICE_ARN} --query 'Service.ServiceUrl' --output text)

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}🌐 Application URL: https://${SERVICE_URL}${NC}"
echo -e "${GREEN}📊 AWS Console: https://${AWS_REGION}.console.aws.amazon.com/apprunner/home?region=${AWS_REGION}#/services${NC}"
echo ""
echo "📝 Next steps:"
echo "1. Visit your application URL to test the deployment"
echo "2. Check CloudWatch logs for any issues"
echo "3. Configure custom domain if needed"
echo "4. Set up monitoring and alerts"
echo ""

# Cleanup temporary files
rm -f apprunner-service.json

echo -e "${GREEN}✅ Deployment script completed${NC}"