# AWS Deployment Guide

Deploy the AI Customer Service Platform to Amazon Web Services using various AWS services.

## Deployment Options

### 1. AWS App Runner (Recommended for Quick Start)
- **Best for**: Rapid deployment, automatic scaling
- **Cost**: Pay-per-use, scales to zero
- **Setup time**: 5-10 minutes

### 2. Amazon ECS with Fargate
- **Best for**: Production workloads, container orchestration
- **Cost**: Predictable pricing, always-on containers
- **Setup time**: 15-30 minutes

### 3. Amazon EKS (Kubernetes)
- **Best for**: Large scale, complex deployments
- **Cost**: Higher (EKS cluster costs + compute)
- **Setup time**: 30-60 minutes

### 4. AWS Lambda + API Gateway
- **Best for**: Serverless, event-driven architecture
- **Cost**: Pay-per-request, very cost effective
- **Setup time**: 20-40 minutes

## Prerequisites

### 1. AWS CLI Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region, and Output format
```

### 2. Required AWS Services
- **ECR** (Elastic Container Registry) - For Docker images
- **VPC** - For networking (can use default)
- **IAM** - For permissions
- **CloudWatch** - For logging and monitoring

## Quick Start: AWS App Runner

### Step 1: Build and Push Docker Image
```bash
# Run the deployment script
./deploy-to-aws-apprunner.sh

# Or manually:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker build -t ai-customer-service .
docker tag ai-customer-service:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-customer-service:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-customer-service:latest
```

### Step 2: Create App Runner Service
```bash
aws apprunner create-service --cli-input-json file://apprunner-service.json
```

### Step 3: Access Your Application
The App Runner service will provide a URL like: `https://xxx.us-east-1.awsapprunner.com`

## Production Deployment: ECS + Fargate

### Step 1: Infrastructure Setup
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name ai-customer-service-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service --cli-input-json file://ecs-service.json
```

### Step 2: Load Balancer Setup
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer --cli-input-json file://alb-config.json

# Create target group and listeners
aws elbv2 create-target-group --cli-input-json file://target-group.json
```

## Serverless Deployment: Lambda + API Gateway

### Step 1: Package Lambda Function
```bash
# Install dependencies and package
pip install -r requirements.txt -t lambda_package/
cp streamlit_app.py mcp_agent.py knowledge_service.py lambda_package/

# Create deployment package
cd lambda_package && zip -r ../lambda-deployment.zip . && cd ..
```

### Step 2: Deploy Lambda
```bash
aws lambda create-function --cli-input-json file://lambda-function.json
```

## Environment Variables

Set these environment variables in your AWS service:

```bash
# Required
OLLAMA_BASE_URL=http://ollama-service:11434  # Or external Ollama endpoint
ENVIRONMENT=production
LOG_LEVEL=INFO

# Optional
STREAMLIT_SERVER_PORT=8501
CHROMA_DB_PATH=/app/chroma_db
KNOWLEDGE_BASE_PATH=/app/knowledge_base_pdfs

# AWS-specific
AWS_REGION=us-east-1
CLOUDWATCH_LOG_GROUP=/aws/ecs/ai-customer-service
```

## Monitoring and Logging

### CloudWatch Integration
- **Logs**: Automatically collected from containers
- **Metrics**: CPU, memory, request count, response time
- **Alarms**: Set up alerts for high error rates or response times

### Custom Metrics
```python
import boto3
cloudwatch = boto3.client('cloudwatch')

# Example: Log custom application metrics
cloudwatch.put_metric_data(
    Namespace='AI-CustomerService',
    MetricData=[
        {
            'MetricName': 'ResponseTime',
            'Value': response_time,
            'Unit': 'Seconds'
        }
    ]
)
```

## Security Best Practices

### 1. IAM Roles and Policies
- Use least-privilege IAM roles
- Separate roles for different services
- Enable CloudTrail for audit logging

### 2. Network Security
- Deploy in private subnets
- Use Security Groups to restrict access
- Enable VPC Flow Logs

### 3. Data Security
- Encrypt data at rest (EBS, S3)
- Use AWS Secrets Manager for sensitive data
- Enable encryption in transit

## Cost Optimization

### 1. Right-sizing
- Start with smaller instances (t3.small)
- Use Auto Scaling to match demand
- Consider Spot Instances for development

### 2. Storage Optimization
- Use EFS for shared storage
- Implement S3 lifecycle policies
- Use CloudWatch Logs retention policies

### 3. Monitoring Costs
- Set up billing alerts
- Use AWS Cost Explorer
- Tag resources for cost tracking

## Scaling Configuration

### Auto Scaling Targets
```json
{
  "TargetValue": 70.0,
  "ScaleOutCooldown": 300,
  "ScaleInCooldown": 300,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  }
}
```

### Load Balancer Health Checks
```json
{
  "HealthCheckPath": "/health",
  "HealthCheckIntervalSeconds": 30,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3,
  "HealthCheckTimeoutSeconds": 5
}
```

## Troubleshooting

### Common Issues
1. **ECR Authentication Failed**
   - Ensure AWS CLI is configured correctly
   - Check ECR repository permissions

2. **Task Definition Registration Failed**
   - Validate JSON syntax
   - Check IAM permissions for ECS

3. **Service Start Failed**
   - Check CloudWatch logs
   - Verify environment variables
   - Ensure proper security group configuration

### Debug Commands
```bash
# Check ECS service status
aws ecs describe-services --cluster ai-customer-service-cluster --services ai-customer-service

# View CloudWatch logs
aws logs get-log-events --log-group-name /ecs/ai-customer-service --log-stream-name STREAM_NAME

# Check task health
aws ecs describe-tasks --cluster ai-customer-service-cluster --tasks TASK_ARN
```

## Next Steps

After successful deployment:
1. Set up CloudWatch dashboards for monitoring
2. Configure Auto Scaling policies
3. Set up CI/CD pipeline with AWS CodePipeline
4. Implement blue-green deployments
5. Add AWS WAF for web application firewall
6. Set up Route 53 for custom domain