# Microsoft Azure Deployment Guide

Deploy the AI Customer Service Platform to Microsoft Azure using various Azure services.

## Deployment Options

### 1. Azure Container Instances (ACI) - Recommended for Quick Start
- **Best for**: Simple container deployments, development/testing
- **Cost**: Pay-per-second, no infrastructure management
- **Setup time**: 5-10 minutes

### 2. Azure Container Apps
- **Best for**: Serverless containers with auto-scaling
- **Cost**: Pay-per-use with generous free tier
- **Setup time**: 10-15 minutes

### 3. Azure Kubernetes Service (AKS)
- **Best for**: Production workloads, complex orchestration
- **Cost**: Cluster management + compute costs
- **Setup time**: 20-30 minutes

### 4. Azure Web Apps for Containers
- **Best for**: PaaS deployment with minimal configuration
- **Cost**: App Service Plan pricing
- **Setup time**: 10-20 minutes

### 5. Azure Functions (Serverless)
- **Best for**: Event-driven, serverless functions
- **Cost**: Consumption-based pricing
- **Setup time**: 15-25 minutes

## Prerequisites

### 1. Azure CLI Setup
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-name"
```

### 2. Set Environment Variables
```bash
export RESOURCE_GROUP=ai-customer-service-rg
export LOCATION=eastus
export ACR_NAME=aicustomerserviceacr
export APP_NAME=ai-customer-service
```

### 3. Create Resource Group
```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

## Quick Start: Azure Container Instances

### Step 1: Create Azure Container Registry
```bash
# Create ACR
az acr create --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Login to ACR
az acr login --name $ACR_NAME
```

### Step 2: Build and Push Image
```bash
# Run deployment script
./deploy-to-azure-aci.sh

# Or manually build and push
docker build -t $ACR_NAME.azurecr.io/ai-customer-service:latest .
docker push $ACR_NAME.azurecr.io/ai-customer-service:latest
```

### Step 3: Deploy to Container Instances
```bash
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --image $ACR_NAME.azurecr.io/ai-customer-service:latest \
    --registry-login-server $ACR_NAME.azurecr.io \
    --registry-username $ACR_NAME \
    --registry-password $(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv) \
    --dns-name-label $APP_NAME-$(date +%s) \
    --ports 8501 \
    --environment-variables ENVIRONMENT=production LOG_LEVEL=INFO \
    --cpu 1 \
    --memory 2
```

## Production Deployment: Azure Container Apps

### Step 1: Create Container Apps Environment
```bash
# Install Container Apps extension
az extension add --name containerapp

# Create Container Apps environment
az containerapp env create \
    --name ai-customer-service-env \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
```

### Step 2: Deploy Container App
```bash
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment ai-customer-service-env \
    --image $ACR_NAME.azurecr.io/ai-customer-service:latest \
    --registry-server $ACR_NAME.azurecr.io \
    --registry-username $ACR_NAME \
    --registry-password $(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv) \
    --target-port 8501 \
    --ingress external \
    --min-replicas 0 \
    --max-replicas 10 \
    --cpu 0.5 \
    --memory 1Gi \
    --env-vars ENVIRONMENT=production LOG_LEVEL=INFO
```

## Enterprise Deployment: Azure Kubernetes Service (AKS)

### Step 1: Create AKS Cluster
```bash
# Create AKS cluster
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name ai-customer-service-aks \
    --node-count 3 \
    --enable-addons monitoring \
    --enable-managed-identity \
    --attach-acr $ACR_NAME \
    --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name ai-customer-service-aks
```

### Step 2: Deploy to AKS
```bash
# Update image in deployment file
sed -i "s/ACR_NAME/$ACR_NAME/g" aks-deployment.yaml

# Deploy to Kubernetes
kubectl apply -f aks-deployment.yaml
```

## PaaS Deployment: Azure Web Apps

### Step 1: Create App Service Plan
```bash
az appservice plan create \
    --name ai-customer-service-plan \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux
```

### Step 2: Create Web App
```bash
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan ai-customer-service-plan \
    --name $APP_NAME-webapp \
    --deployment-container-image-name $ACR_NAME.azurecr.io/ai-customer-service:latest

# Configure container settings
az webapp config container set \
    --name $APP_NAME-webapp \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_NAME.azurecr.io/ai-customer-service:latest \
    --docker-registry-server-url https://$ACR_NAME.azurecr.io \
    --docker-registry-server-user $ACR_NAME \
    --docker-registry-server-password $(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
```

## Serverless Deployment: Azure Functions

### Step 1: Create Function App
```bash
az storage account create \
    --name aicustomerstorage$(date +%s) \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --sku Standard_LRS

az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location $LOCATION \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --name $APP_NAME-function \
    --storage-account aicustomerstorage$(date +%s)
```

### Step 2: Deploy Function Code
```bash
# Package and deploy
func azure functionapp publish $APP_NAME-function
```

## Environment Configuration

### Application Settings (Container Apps)
```bash
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars \
        ENVIRONMENT=production \
        LOG_LEVEL=INFO \
        STREAMLIT_SERVER_PORT=8501 \
        OLLAMA_BASE_URL=https://your-ollama-endpoint
```

### Key Vault Integration
```bash
# Create Key Vault
az keyvault create \
    --name ai-customer-keyvault \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Store secrets
az keyvault secret set \
    --vault-name ai-customer-keyvault \
    --name api-key \
    --value "your-secret-api-key"

# Grant access to Container App
az containerapp identity assign \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --system-assigned

# Use secret in Container App
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars API_KEY=secretref:api-key
```

## Monitoring and Logging

### Application Insights Setup
```bash
# Create Application Insights
az monitor app-insights component create \
    --app ai-customer-service-insights \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app ai-customer-service-insights \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey -o tsv)

# Add to container environment
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSTRUMENTATION_KEY"
```

### Log Analytics Integration
```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --workspace-name ai-customer-service-logs \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION
```

## Auto-scaling Configuration

### Container Apps Auto-scaling
```bash
# Set scaling rules
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 1 \
    --max-replicas 20 \
    --scale-rule-name http-rule \
    --scale-rule-type http \
    --scale-rule-http-concurrent-requests 10
```

### AKS Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-customer-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-customer-service
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Security Configuration

### Network Security Groups
```bash
# Create NSG for AKS
az network nsg create \
    --resource-group $RESOURCE_GROUP \
    --name ai-customer-service-nsg

# Add rule for HTTPS traffic
az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name ai-customer-service-nsg \
    --name allow-https \
    --protocol tcp \
    --priority 1001 \
    --destination-port-range 443 \
    --access allow
```

### Managed Identity
```bash
# Assign managed identity to Container App
az containerapp identity assign \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --system-assigned

# Grant permissions to access Key Vault
az keyvault set-policy \
    --name ai-customer-keyvault \
    --object-id $(az containerapp identity show --name $APP_NAME --resource-group $RESOURCE_GROUP --query principalId -o tsv) \
    --secret-permissions get list
```

## CI/CD Pipeline with Azure DevOps

### Azure Pipeline Configuration
```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  imageRepository: 'ai-customer-service'
  containerRegistry: 'aicustomerserviceacr.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)'

stages:
- stage: Build
  displayName: Build and push stage
  jobs:
  - job: Build
    displayName: Build
    steps:
    - task: Docker@2
      displayName: Build and push image
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  jobs:
  - deployment: Deploy
    displayName: Deploy
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureContainerApps@1
            displayName: Deploy to Container Apps
            inputs:
              azureSubscription: $(azureServiceConnection)
              containerAppName: $(containerAppName)
              resourceGroup: $(resourceGroupName)
              imageToDeploy: $(containerRegistry)/$(imageRepository):$(tag)
```

## Cost Optimization

### Container Apps Pricing
```bash
# Set minimum replicas to 0 for cost savings
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 0 \
    --max-replicas 10
```

### AKS Node Pool Optimization
```bash
# Add spot node pool for cost savings
az aks nodepool add \
    --resource-group $RESOURCE_GROUP \
    --cluster-name ai-customer-service-aks \
    --name spotnodepool \
    --priority Spot \
    --eviction-policy Delete \
    --spot-max-price -1 \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 3 \
    --node-vm-size Standard_DS2_v2
```

## Backup and Disaster Recovery

### Container Registry Geo-replication
```bash
# Enable geo-replication
az acr replication create \
    --registry $ACR_NAME \
    --location westus2
```

### Application Backup
```bash
# Create backup for Container App configuration
az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output json > app-backup.json
```

## Troubleshooting

### Common Issues

1. **Container Registry Access Denied**
   ```bash
   # Check ACR credentials
   az acr credential show --name $ACR_NAME
   
   # Enable admin user if needed
   az acr update --name $ACR_NAME --admin-enabled true
   ```

2. **Container App Not Starting**
   ```bash
   # Check logs
   az containerapp logs show \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP
   ```

3. **AKS Pod Issues**
   ```bash
   # Check pod status
   kubectl get pods -o wide
   kubectl describe pod pod-name
   ```

### Debug Commands
```bash
# Container Apps logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Container Instances logs
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME

# Web App logs
az webapp log tail \
  --name $APP_NAME-webapp \
  --resource-group $RESOURCE_GROUP
```

## Performance Optimization

### Content Delivery Network (CDN)
```bash
# Create CDN profile
az cdn profile create \
    --name ai-customer-service-cdn \
    --resource-group $RESOURCE_GROUP \
    --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
    --name ai-customer-service-endpoint \
    --profile-name ai-customer-service-cdn \
    --resource-group $RESOURCE_GROUP \
    --origin your-app-domain.azurecontainerapps.io \
    --origin-host-header your-app-domain.azurecontainerapps.io
```

### Application Gateway Setup
```bash
# Create Application Gateway for advanced routing
az network application-gateway create \
    --name ai-customer-service-gateway \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --vnet-name gateway-vnet \
    --subnet gateway-subnet \
    --capacity 2 \
    --sku Standard_v2 \
    --http-settings-cookie-based-affinity Disabled \
    --frontend-port 80 \
    --http-settings-port 8501 \
    --http-settings-protocol Http
```

## Custom Domain Configuration

### Container Apps Custom Domain
```bash
# Add custom domain
az containerapp hostname add \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --hostname your-domain.com

# Bind SSL certificate
az containerapp ssl upload \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --certificate-file certificate.pfx \
    --certificate-password password \
    --hostname your-domain.com
```

## Next Steps

After successful deployment:
1. Set up Azure Monitor dashboards and alerts
2. Configure Azure Front Door for global load balancing
3. Implement Azure WAF for web application firewall
4. Set up Azure Backup for data protection
5. Configure Azure Policy for compliance
6. Implement proper DevOps practices with Azure DevOps
7. Set up Azure Security Center for security monitoring