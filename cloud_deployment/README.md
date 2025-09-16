# Cloud Deployment Guide

This directory contains comprehensive deployment guides and automation scripts for deploying the AI Customer Service Platform to major cloud providers.

## 🚀 Quick Start

### Universal Deployment Script
Use the universal deployment script for the easiest deployment experience:

```bash
# Interactive deployment (recommended)
./cloud_deployment/scripts/cloud-deploy.sh interactive

# Deploy directly to specific cloud
./cloud_deployment/scripts/cloud-deploy.sh aws
./cloud_deployment/scripts/cloud-deploy.sh gcp
./cloud_deployment/scripts/cloud-deploy.sh azure

# Check prerequisites
./cloud_deployment/scripts/cloud-deploy.sh --check
```

### One-Command Deployment
```bash
# AWS (App Runner)
./cloud_deployment/aws/deploy-to-aws-apprunner.sh

# Google Cloud (Cloud Run)  
./cloud_deployment/gcp/deploy-to-cloud-run.sh

# Azure (Container Instances)
./cloud_deployment/azure/deploy-to-azure-aci.sh
```

## 📁 Directory Structure

```
cloud_deployment/
├── README.md                          # This file
├── scripts/
│   └── cloud-deploy.sh               # Universal deployment script
├── aws/
│   ├── README.md                      # AWS deployment guide
│   ├── deploy-to-aws-apprunner.sh    # AWS App Runner deployment
│   ├── ecs-task-definition.json      # ECS/Fargate configuration
│   └── lambda-function.json          # Lambda deployment config
├── gcp/
│   ├── README.md                      # GCP deployment guide
│   ├── deploy-to-cloud-run.sh        # Cloud Run deployment
│   └── gke-deployment.yaml           # Kubernetes manifests
└── azure/
    ├── README.md                      # Azure deployment guide
    ├── deploy-to-azure-aci.sh         # Container Instances deployment
    └── aks-deployment.yaml            # AKS Kubernetes manifests
```

## 🌍 Cloud Provider Comparison

| Feature | AWS | GCP | Azure | Best For |
|---------|-----|-----|-------|----------|
| **Quick Start** | App Runner | Cloud Run | Container Instances | First-time deployments |
| **Serverless Containers** | App Runner | Cloud Run | Container Apps | Auto-scaling applications |
| **Kubernetes** | EKS | GKE | AKS | Enterprise/Complex deployments |
| **Functions** | Lambda | Cloud Functions | Functions | Event-driven architecture |
| **Setup Time** | 5-10 min | 5-10 min | 5-10 min | Fast deployment |
| **Auto-scaling** | ✅ | ✅ | ✅ | Variable traffic |
| **Free Tier** | Limited | Generous | Good | Cost optimization |

## 🛠️ Prerequisites

### General Requirements
- Docker installed and running
- Git for version control
- Application source code
- Basic understanding of containerization

### Cloud-Specific CLI Tools

#### AWS
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
```

#### Google Cloud Platform
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud init
gcloud auth login
```

#### Microsoft Azure
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login
```

## 🎯 Recommended Deployment Paths

### For Development/Testing
1. **Quick Start**: Use Container Instances/Cloud Run
2. **Low Traffic**: Start with minimal resources
3. **Experimentation**: Use free tiers

### For Production
1. **High Availability**: Use Kubernetes (EKS/GKE/AKS)
2. **Auto-scaling**: Configure HPA and cluster auto-scaling
3. **Monitoring**: Set up comprehensive observability
4. **Security**: Enable encryption, network policies, secrets management

### For Enterprise
1. **Multi-region**: Deploy across multiple regions
2. **Compliance**: Enable audit logging and compliance features
3. **Integration**: Connect with existing enterprise systems
4. **Disaster Recovery**: Implement backup and recovery procedures

## 🔧 Configuration Management

### Environment Variables
Common environment variables across all cloud providers:

```bash
# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# AI Configuration
OLLAMA_BASE_URL=http://ollama-service:11434
MODEL_NAME=llama3.2

# Database Configuration
CHROMA_DB_PATH=/app/chroma_db
KNOWLEDGE_BASE_PATH=/app/knowledge_base_pdfs

# Cloud-specific
AWS_REGION=us-east-1
GCP_PROJECT_ID=your-project
AZURE_RESOURCE_GROUP=your-rg
```

### Secrets Management
- **AWS**: Use AWS Secrets Manager or Parameter Store
- **GCP**: Use Secret Manager
- **Azure**: Use Key Vault

## 📊 Monitoring and Observability

### Built-in Cloud Monitoring
- **AWS**: CloudWatch Logs, Metrics, and Alarms
- **GCP**: Cloud Monitoring, Cloud Logging
- **Azure**: Azure Monitor, Application Insights

### Application Health Checks
All deployments include health check endpoints:
- **Health Check**: `/_stcore/health`
- **Metrics**: Custom application metrics
- **Logs**: Structured logging with correlation IDs

## 💰 Cost Optimization

### General Tips
1. **Right-size Resources**: Start small and scale up
2. **Use Auto-scaling**: Scale down during low usage
3. **Monitor Costs**: Set up billing alerts
4. **Reserved Instances**: For predictable workloads

### Cloud-Specific Optimization
- **AWS**: Use Spot instances, right-size EC2
- **GCP**: Use preemptible instances, committed use discounts
- **Azure**: Use spot VMs, reserved instances

## 🔒 Security Best Practices

### Network Security
- Deploy in private subnets when possible
- Use security groups/firewall rules
- Enable VPC/VNET flow logs

### Application Security
- Use non-root containers
- Scan images for vulnerabilities
- Keep dependencies updated
- Enable encryption at rest and in transit

### Access Control
- Use IAM roles instead of access keys
- Implement least privilege principle
- Enable audit logging
- Use managed identities where possible

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
# AWS: aws logs tail /aws/apprunner/your-service
# GCP: gcloud logging read "resource.type=cloud_run_revision"
# Azure: az container logs --resource-group RG --name NAME
```

#### Health Check Failing
- Verify port configuration (8501)
- Check application startup time
- Ensure health endpoint is accessible

#### Performance Issues
- Monitor CPU and memory usage
- Check network latency
- Review application logs for errors

### Debug Commands

#### AWS
```bash
# App Runner logs
aws apprunner describe-service --service-arn YOUR_ARN
aws logs tail /aws/apprunner/your-service

# ECS logs
aws ecs describe-services --cluster CLUSTER --services SERVICE
```

#### GCP
```bash
# Cloud Run logs
gcloud run services describe SERVICE --region=REGION
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

#### Azure
```bash
# Container Instances
az container show --resource-group RG --name NAME
az container logs --resource-group RG --name NAME
```

## 📚 Additional Resources

### Documentation Links
- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Azure Container Instances Documentation](https://docs.microsoft.com/en-us/azure/container-instances/)

### Training and Certification
- AWS Solutions Architect
- Google Cloud Professional Cloud Architect
- Azure Solutions Architect Expert

### Community Resources
- [AWS Samples GitHub](https://github.com/aws-samples)
- [Google Cloud Samples](https://github.com/GoogleCloudPlatform)
- [Azure Samples](https://github.com/Azure-Samples)

## 🤝 Support

For deployment issues:
1. Check the specific cloud provider README
2. Review troubleshooting sections
3. Check cloud provider status pages
4. Consult cloud provider documentation
5. Use cloud provider support channels

## 🔄 Updates and Maintenance

### Keeping Deployments Updated
1. **Container Images**: Regularly update base images
2. **Dependencies**: Keep Python packages current
3. **Cloud Services**: Update to latest service versions
4. **Security Patches**: Apply security updates promptly

### Automated Updates
Consider setting up automated deployment pipelines:
- **AWS**: CodePipeline + CodeBuild
- **GCP**: Cloud Build + Cloud Deploy
- **Azure**: Azure DevOps Pipelines

---

**Ready to deploy?** Choose your cloud provider and follow the specific deployment guide in the respective subdirectory!