# Google Cloud Platform Deployment Guide

Deploy the AI Customer Service Platform to Google Cloud Platform using various GCP services.

## Deployment Options

### 1. Cloud Run (Recommended for Quick Start)
- **Best for**: Serverless containers, automatic scaling
- **Cost**: Pay-per-request, scales to zero
- **Setup time**: 5-10 minutes

### 2. Google Kubernetes Engine (GKE)
- **Best for**: Production workloads, complex deployments
- **Cost**: Cluster management + compute costs
- **Setup time**: 15-30 minutes

### 3. Compute Engine + Docker
- **Best for**: Traditional VM deployments, full control
- **Cost**: VM instance costs
- **Setup time**: 10-20 minutes

### 4. Cloud Functions (Serverless)
- **Best for**: Event-driven, lightweight functions
- **Cost**: Pay-per-invocation
- **Setup time**: 15-25 minutes

## Prerequisites

### 1. Google Cloud CLI Setup
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize and authenticate
gcloud init
gcloud auth login
gcloud auth configure-docker
```

### 2. Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 3. Set Project Variables
```bash
export PROJECT_ID=your-project-id
export REGION=us-central1
export SERVICE_NAME=ai-customer-service
```

## Quick Start: Cloud Run

### Step 1: Build and Deploy
```bash
# Run the deployment script
./deploy-to-cloud-run.sh

# Or manually deploy
gcloud run deploy ai-customer-service \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8501 \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO
```

### Step 2: Access Your Application
Cloud Run will provide a URL like: `https://ai-customer-service-xxx.a.run.app`

## Production Deployment: Google Kubernetes Engine (GKE)

### Step 1: Create GKE Cluster
```bash
# Create cluster
gcloud container clusters create ai-customer-service-cluster \
    --zone us-central1-a \
    --num-nodes 3 \
    --enable-autoscaling \
    --min-nodes 1 \
    --max-nodes 10 \
    --enable-autorepair \
    --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials ai-customer-service-cluster --zone us-central1-a
```

### Step 2: Deploy to GKE
```bash
# Build and push image
docker build -t gcr.io/${PROJECT_ID}/ai-customer-service:latest .
docker push gcr.io/${PROJECT_ID}/ai-customer-service:latest

# Deploy to Kubernetes
kubectl apply -f gke-deployment.yaml
kubectl apply -f gke-service.yaml
kubectl apply -f gke-ingress.yaml
```

## VM Deployment: Compute Engine

### Step 1: Create VM Instance
```bash
# Create VM with container-optimized OS
gcloud compute instances create-with-container ai-customer-service-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --container-image=gcr.io/${PROJECT_ID}/ai-customer-service:latest \
    --container-restart-policy=always \
    --container-env=ENVIRONMENT=production,LOG_LEVEL=INFO \
    --tags=http-server,https-server \
    --boot-disk-size=20GB

# Create firewall rule
gcloud compute firewall-rules create allow-streamlit \
    --allow tcp:8501 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Streamlit traffic"
```

## Serverless Deployment: Cloud Functions

### Step 1: Prepare Function Code
```bash
# Create function directory
mkdir cloud_function
cp streamlit_app.py mcp_agent.py knowledge_service.py cloud_function/
cd cloud_function

# Create main.py for Cloud Functions
cat > main.py << 'EOF'
import functions_framework
from streamlit_app import main as streamlit_main

@functions_framework.http
def ai_customer_service(request):
    return streamlit_main(request)
EOF
```

### Step 2: Deploy Function
```bash
gcloud functions deploy ai-customer-service \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=ai_customer_service \
    --trigger=http \
    --allow-unauthenticated \
    --memory=1Gi \
    --timeout=540s
```

## Environment Configuration

### Cloud Run Environment Variables
```bash
gcloud run services update ai-customer-service \
    --region us-central1 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars LOG_LEVEL=INFO \
    --set-env-vars STREAMLIT_SERVER_PORT=8501 \
    --set-env-vars OLLAMA_BASE_URL=https://your-ollama-endpoint
```

### Secrets Management
```bash
# Store sensitive data in Secret Manager
echo -n "your-api-key" | gcloud secrets create api-key --data-file=-

# Use in Cloud Run
gcloud run services update ai-customer-service \
    --region us-central1 \
    --set-secrets API_KEY=api-key:latest
```

## Monitoring and Logging

### Cloud Monitoring Setup
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### Logging Configuration
```python
# Add to your application
import google.cloud.logging

# Setup Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Log structured data
logger = logging.getLogger(__name__)
logger.info("Application started", extra={"component": "main"})
```

## Load Testing and Scaling

### Horizontal Pod Autoscaler (GKE)
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

### Cloud Run Concurrency
```bash
# Set maximum concurrent requests per instance
gcloud run services update ai-customer-service \
    --region us-central1 \
    --concurrency 10 \
    --max-instances 100
```

## Security Configuration

### Identity and Access Management (IAM)
```bash
# Create service account
gcloud iam service-accounts create ai-customer-service \
    --display-name "AI Customer Service"

# Grant necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member "serviceAccount:ai-customer-service@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role "roles/secretmanager.secretAccessor"
```

### VPC Security
```bash
# Create VPC connector for Cloud Run
gcloud compute networks vpc-access connectors create ai-vpc-connector \
    --region us-central1 \
    --subnet default \
    --subnet-project ${PROJECT_ID}

# Use VPC connector
gcloud run services update ai-customer-service \
    --region us-central1 \
    --vpc-connector ai-vpc-connector
```

## CI/CD Pipeline

### Cloud Build Configuration
```yaml
# cloudbuild.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-customer-service:$COMMIT_SHA', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-customer-service:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'ai-customer-service'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ai-customer-service:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/ai-customer-service:$COMMIT_SHA'
```

### GitHub Integration
```bash
# Connect GitHub repository
gcloud builds triggers create github \
    --repo-name=ai-customer-service \
    --repo-owner=your-username \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Cost Optimization

### Resource Allocation
```bash
# Optimize Cloud Run resources
gcloud run services update ai-customer-service \
    --region us-central1 \
    --memory 512Mi \
    --cpu 0.5 \
    --min-instances 0 \
    --max-instances 10
```

### Preemptible Instances (GKE)
```bash
# Create node pool with preemptible instances
gcloud container node-pools create preemptible-pool \
    --cluster ai-customer-service-cluster \
    --zone us-central1-a \
    --preemptible \
    --num-nodes 2 \
    --machine-type e2-medium
```

## Backup and Disaster Recovery

### Cloud SQL Backups (if using database)
```bash
# Enable automated backups
gcloud sql instances patch your-instance \
    --backup-start-time 03:00 \
    --enable-bin-log \
    --backup-location us-central1
```

### Persistent Volume Snapshots (GKE)
```bash
# Create volume snapshot
gcloud compute snapshots create ai-data-snapshot \
    --source-disk your-disk \
    --zone us-central1-a
```

## Troubleshooting

### Common Issues

1. **Cloud Run Cold Starts**
   ```bash
   # Set minimum instances to reduce cold starts
   gcloud run services update ai-customer-service \
       --region us-central1 \
       --min-instances 1
   ```

2. **GKE Pod Scheduling Issues**
   ```bash
   # Check node resources
   kubectl describe nodes
   kubectl top nodes
   ```

3. **Cloud Build Timeout**
   ```bash
   # Increase build timeout
   gcloud builds submit --timeout 20m .
   ```

### Debug Commands
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Check GKE pod status
kubectl get pods -o wide
kubectl logs pod-name -f

# Monitor Cloud Run metrics
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"
```

## Custom Domain Setup

### Cloud Run Custom Domain
```bash
# Map custom domain
gcloud run domain-mappings create \
    --service ai-customer-service \
    --domain your-domain.com \
    --region us-central1
```

### GKE with Ingress
```bash
# Create static IP
gcloud compute addresses create ai-customer-service-ip \
    --global

# Update DNS records to point to the static IP
```

## Performance Optimization

### Caching Strategies
- Use Cloud CDN for static content
- Implement Redis with Cloud Memorystore
- Enable Cloud Run response caching

### Resource Monitoring
```bash
# Set up alerting policies
gcloud alpha monitoring policies create --policy-from-file=alerting-policy.yaml
```

## Next Steps

After successful deployment:
1. Set up Cloud Monitoring dashboards
2. Configure alerting and notification channels
3. Implement Cloud CDN for better performance
4. Set up Cloud Armor for DDoS protection
5. Enable Cloud Security Command Center
6. Implement proper backup and disaster recovery procedures