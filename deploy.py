#!/usr/bin/env python3
"""
Deployment script for Customer Support AI Agent
Supports deployment to various cloud platforms
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports
EXPOSE 8501 11434

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("SUCCESS: Dockerfile created")

def create_start_script():
    """Create startup script for container"""
    start_script = """#!/bin/bash

# Start Ollama in background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull the model
ollama pull llama3.2

# Start Streamlit app
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
"""
    
    with open("start.sh", "w") as f:
        f.write(start_script)
    
    print("SUCCESS: Start script created")

def create_docker_compose():
    """Create docker-compose.yml for easy deployment"""
    compose_content = """
version: '3.8'

services:
  customer-support-ai:
    build: .
    ports:
      - "8501:8501"
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped

volumes:
  ollama_data:
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    print("SUCCESS: Docker Compose file created")

def create_requirements_production():
    """Create production requirements with pinned versions"""
    prod_requirements = """
streamlit==1.28.1
requests==2.31.0
chromadb==0.4.15
pandas==2.1.4
json5==0.9.14
watchdog==3.0.0
"""
    
    with open("requirements-prod.txt", "w") as f:
        f.write(prod_requirements)
    
    print("SUCCESS: Production requirements created")

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("Deploying to Heroku...")
    
    # Create Procfile
    with open("Procfile", "w") as f:
        f.write("web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0\\n")
    
    # Create runtime.txt
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.6\\n")
    
    try:
        # Initialize git repo if needed
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        # Create Heroku app
        app_name = input("Enter Heroku app name (or press Enter for auto-generated): ")
        create_cmd = ["heroku", "create"]
        if app_name:
            create_cmd.append(app_name)
        
        subprocess.run(create_cmd, check=True)
        
        # Deploy
        subprocess.run(["git", "push", "heroku", "main"], check=True)
        
        print("SUCCESS: Deployed to Heroku successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Heroku deployment failed: {e}")

def deploy_to_aws():
    """Deploy to AWS using ECS"""
    print("Deploying to AWS ECS...")
    
    # Create task definition
    task_def = {
        "family": "customer-support-ai",
        "networkMode": "awsvpc",
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "1024",
        "memory": "2048",
        "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
        "containerDefinitions": [
            {
                "name": "customer-support-ai",
                "image": "your-account.dkr.ecr.region.amazonaws.com/customer-support-ai:latest",
                "portMappings": [
                    {
                        "containerPort": 8501,
                        "protocol": "tcp"
                    }
                ],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": "/ecs/customer-support-ai",
                        "awslogs-region": "us-east-1",
                        "awslogs-stream-prefix": "ecs"
                    }
                }
            }
        ]
    }
    
    with open("task-definition.json", "w") as f:
        json.dump(task_def, f, indent=2)
    
    print("SUCCESS: AWS ECS task definition created")
    print("Next steps:")
    print("1. Build and push Docker image to ECR")
    print("2. Create ECS cluster")
    print("3. Register task definition")
    print("4. Create ECS service")

def deploy_to_gcp():
    """Deploy to Google Cloud Platform"""
    print("Deploying to Google Cloud Platform...")
    
    # Create app.yaml for App Engine
    app_yaml = """
runtime: python311

env_variables:
  OLLAMA_HOST: "0.0.0.0"

automatic_scaling:
  min_instances: 1
  max_instances: 10

resources:
  cpu: 2
  memory_gb: 4
"""
    
    with open("app.yaml", "w") as f:
        f.write(app_yaml)
    
    print("SUCCESS: Google Cloud App Engine config created")
    print("Deploy with: gcloud app deploy")

def create_kubernetes_manifests():
    """Create Kubernetes deployment manifests"""
    
    # Deployment manifest
    deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-support-ai
  labels:
    app: customer-support-ai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: customer-support-ai
  template:
    metadata:
      labels:
        app: customer-support-ai
    spec:
      containers:
      - name: customer-support-ai
        image: customer-support-ai:latest
        ports:
        - containerPort: 8501
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: customer-support-ai-service
spec:
  selector:
    app: customer-support-ai
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
  type: LoadBalancer
"""
    
    with open("k8s-deployment.yaml", "w") as f:
        f.write(deployment)
    
    print("SUCCESS: Kubernetes manifests created")

def setup_monitoring():
    """Create monitoring and health check configurations"""
    
    # Health check endpoint for Streamlit
    health_check = """
import streamlit as st
import requests

def health_check():
    try:
        # Check Ollama connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "ollama": "connected"}
        else:
            return {"status": "unhealthy", "ollama": "disconnected"}
    except:
        return {"status": "unhealthy", "ollama": "error"}

if __name__ == "__main__":
    st.write(health_check())
"""
    
    with open("health_check.py", "w") as f:
        f.write(health_check)
    
    print("SUCCESS: Health check endpoint created")

def main():
    """Main deployment function"""
    print("Customer Support AI Agent - Deployment Tool")
    print("=" * 60)
    
    print("Choose deployment option:")
    print("1. Create Docker files")
    print("2. Deploy to Heroku")
    print("3. Deploy to AWS ECS")
    print("4. Deploy to Google Cloud")
    print("5. Create Kubernetes manifests")
    print("6. Setup monitoring")
    print("7. All deployment files")
    
    choice = input("\\nEnter choice (1-7): ").strip()
    
    if choice == "1":
        create_dockerfile()
        create_start_script()
        create_docker_compose()
        create_requirements_production()
    elif choice == "2":
        deploy_to_heroku()
    elif choice == "3":
        deploy_to_aws()
    elif choice == "4":
        deploy_to_gcp()
    elif choice == "5":
        create_kubernetes_manifests()
    elif choice == "6":
        setup_monitoring()
    elif choice == "7":
        print("Creating all deployment files...")
        create_dockerfile()
        create_start_script()
        create_docker_compose()
        create_requirements_production()
        deploy_to_aws()
        deploy_to_gcp()
        create_kubernetes_manifests()
        setup_monitoring()
        print("SUCCESS: All deployment files created!")
    else:
        print("ERROR: Invalid choice")
        return
    
    print("\\nDeployment preparation complete!")
    print("\\nAdditional Resources:")
    print("- Docker: https://docs.docker.com")
    print("- Heroku: https://devcenter.heroku.com")
    print("- AWS ECS: https://docs.aws.amazon.com/ecs")
    print("- Google Cloud: https://cloud.google.com/docs")
    print("- Kubernetes: https://kubernetes.io/docs")

if __name__ == "__main__":
    main()
