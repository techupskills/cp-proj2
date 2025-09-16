#!/bin/bash

# Azure Container Instances Deployment Script for AI Customer Service Platform
# This script deploys the application to Azure Container Instances with minimal configuration

set -e

# Configuration
RESOURCE_GROUP=${RESOURCE_GROUP:-ai-customer-service-rg}
LOCATION=${LOCATION:-eastus}
ACR_NAME=${ACR_NAME:-aicustomerserviceacr$(date +%s)}
APP_NAME=${APP_NAME:-ai-customer-service}
DNS_NAME_LABEL=${DNS_NAME_LABEL:-$APP_NAME-$(date +%s)}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Azure Container Instances deployment for AI Customer Service Platform${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Please install Azure CLI first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check if user is logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure. Please run 'az login' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Display configuration
echo "Configuration:"
echo "  Resource Group: ${RESOURCE_GROUP}"
echo "  Location: ${LOCATION}"
echo "  ACR Name: ${ACR_NAME}"
echo "  App Name: ${APP_NAME}"
echo "  DNS Label: ${DNS_NAME_LABEL}"
echo ""

# Step 1: Create Resource Group
echo -e "${YELLOW}📁 Creating resource group...${NC}"

if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✅ Resource group already exists${NC}"
else
    az group create --name $RESOURCE_GROUP --location $LOCATION
    echo -e "${GREEN}✅ Resource group created${NC}"
fi

# Step 2: Create Azure Container Registry
echo -e "${YELLOW}📦 Setting up Azure Container Registry...${NC}"

if az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✅ ACR already exists${NC}"
else
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true
    echo -e "${GREEN}✅ ACR created${NC}"
fi

# Step 3: Login to ACR
echo -e "${YELLOW}🔐 Logging in to ACR...${NC}"

az acr login --name $ACR_NAME

echo -e "${GREEN}✅ Logged in to ACR${NC}"

# Step 4: Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"

# Create optimized Dockerfile for Azure if it doesn't exist
if [ ! -f "Dockerfile.azure" ]; then
    cat > Dockerfile.azure << 'EOF'
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

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
fi

docker build -f Dockerfile.azure -t $ACR_NAME.azurecr.io/ai-customer-service:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Step 5: Push image to ACR
echo -e "${YELLOW}📤 Pushing image to ACR...${NC}"

docker push $ACR_NAME.azurecr.io/ai-customer-service:latest

echo -e "${GREEN}✅ Image pushed successfully${NC}"

# Step 6: Get ACR credentials
echo -e "${YELLOW}🔑 Getting ACR credentials...${NC}"

ACR_USERNAME=$ACR_NAME
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Step 7: Deploy to Azure Container Instances
echo -e "${YELLOW}🚀 Deploying to Azure Container Instances...${NC}"

az container create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --image $ACR_NAME.azurecr.io/ai-customer-service:latest \
    --registry-login-server $ACR_NAME.azurecr.io \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label $DNS_NAME_LABEL \
    --ports 8501 \
    --environment-variables \
        ENVIRONMENT=production \
        LOG_LEVEL=INFO \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    --cpu 1 \
    --memory 2 \
    --restart-policy Always

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Step 8: Get container information
echo -e "${YELLOW}📊 Getting container information...${NC}"

# Wait for container to be ready
echo "Waiting for container to start..."
sleep 30

CONTAINER_INFO=$(az container show --resource-group $RESOURCE_GROUP --name $APP_NAME --output json)
CONTAINER_STATE=$(echo $CONTAINER_INFO | jq -r '.containers[0].instanceView.currentState.state')
FQDN=$(echo $CONTAINER_INFO | jq -r '.ipAddress.fqdn')
IP_ADDRESS=$(echo $CONTAINER_INFO | jq -r '.ipAddress.ip')

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}🌐 Application URL: http://${FQDN}:8501${NC}"
echo -e "${GREEN}📍 IP Address: ${IP_ADDRESS}${NC}"
echo -e "${GREEN}📊 Container State: ${CONTAINER_STATE}${NC}"
echo -e "${GREEN}🏢 Azure Portal: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourcegroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}${NC}"
echo ""

# Step 9: Test deployment
echo -e "${YELLOW}🔍 Testing deployment...${NC}"

# Wait a bit more for the application to fully start
sleep 30

# Test the health endpoint
HEALTH_URL="http://${FQDN}:8501/_stcore/health"
if curl -f -s --connect-timeout 10 "${HEALTH_URL}" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed - Application is running${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed, but container might still be starting up${NC}"
    echo "You can check the logs with:"
    echo "  az container logs --resource-group ${RESOURCE_GROUP} --name ${APP_NAME}"
fi

echo ""
echo "📝 Next steps:"
echo "1. Visit your application URL to test the deployment"
echo "2. Check container logs if needed:"
echo "   az container logs --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --follow"
echo "3. Monitor container metrics:"
echo "   az container show --resource-group ${RESOURCE_GROUP} --name ${APP_NAME} --query containers[0].instanceView"
echo "4. Configure custom domain if needed"
echo "5. Set up monitoring and alerts with Azure Monitor"
echo ""

# Optional: Set up monitoring
read -p "Would you like to set up basic monitoring with Azure Monitor? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚙️ Setting up Azure Monitor...${NC}"
    
    # Create Log Analytics workspace
    WORKSPACE_NAME="${APP_NAME}-logs"
    az monitor log-analytics workspace create \
        --workspace-name $WORKSPACE_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        || echo "Workspace might already exist"
    
    echo -e "${GREEN}✅ Basic monitoring configured${NC}"
    echo "View logs at: https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourcegroups/${RESOURCE_GROUP}/providers/Microsoft.OperationalInsights/workspaces/${WORKSPACE_NAME}"
fi

# Optional: Configure automatic restarts
read -p "Would you like to configure automatic restart on failure? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚙️ The container is already configured with restart policy 'Always'${NC}"
    echo -e "${GREEN}✅ Automatic restart is enabled${NC}"
fi

# Optional: Scale up resources
read -p "Would you like to scale up resources for better performance? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚡ Scaling up container resources...${NC}"
    
    # Delete current container
    az container delete --resource-group $RESOURCE_GROUP --name $APP_NAME --yes
    
    # Create with higher resources
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --image $ACR_NAME.azurecr.io/ai-customer-service:latest \
        --registry-login-server $ACR_NAME.azurecr.io \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --dns-name-label $DNS_NAME_LABEL \
        --ports 8501 \
        --environment-variables \
            ENVIRONMENT=production \
            LOG_LEVEL=INFO \
            STREAMLIT_SERVER_PORT=8501 \
            STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        --cpu 2 \
        --memory 4 \
        --restart-policy Always
    
    echo -e "${GREEN}✅ Container scaled up to 2 CPUs and 4GB memory${NC}"
fi

# Cleanup temporary files
rm -f Dockerfile.azure

echo ""
echo -e "${GREEN}✅ Deployment script completed${NC}"
echo -e "${GREEN}🚀 Your AI Customer Service Platform is now live at: http://${FQDN}:8501${NC}"