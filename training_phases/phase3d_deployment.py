#!/usr/bin/env python3
"""
Phase 3d: Deployment & Production (90 min)
Day 3 - Accelerating the SDLC: Deploying AI-powered applications to production

Learning Objectives:
- Production deployment strategies for AI applications
- Container orchestration and scaling considerations
- Monitoring, logging, and observability patterns
- Security, authentication, and data privacy
- Performance optimization and cost management
- CI/CD pipelines for AI applications

This module covers the final step: deploying AI applications to production
with proper monitoring, security, and scaling capabilities.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

# Import previous phase capabilities
sys.path.append(os.path.dirname(__file__))

try:
    from phase1a_basic_llm import BasicLLMClient
    from phase1d_basic_rag import BasicRAGSystem
    from phase2a_simple_agent import SimpleAgent
    from phase2d_mcp_client import MCPEnabledAgent
    from phase3c_integration import IntegratedAIPlatform
    LLM_AVAILABLE = True
    RAG_AVAILABLE = True
    AGENT_AVAILABLE = True
    MCP_AVAILABLE = True
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    LLM_AVAILABLE = False
    RAG_AVAILABLE = False
    AGENT_AVAILABLE = False
    MCP_AVAILABLE = False
    INTEGRATION_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deployment")

class ProductionDeploymentManager:
    """
    Production deployment manager for AI applications.
    Handles containerization, orchestration, and deployment automation.
    """
    
    def __init__(self, project_name: str = "ai-customer-service"):
        """Initialize deployment manager."""
        self.project_name = project_name
        self.deployment_configs = {}
        self.containers = {}
        self.monitoring_active = False
        self.deployment_log = []
        
        logger.info(f"Production deployment manager initialized for {project_name}")
    
    def generate_dockerfile(self, app_type: str = "streamlit") -> str:
        """Generate Dockerfile for the application."""
        if app_type == "streamlit":
            dockerfile_content = '''# Production Dockerfile for AI Customer Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
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

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
'''
        elif app_type == "mcp-server":
            dockerfile_content = '''# Production Dockerfile for MCP Server
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose MCP port
EXPOSE 3000

ENV PYTHONPATH=/app

# Run MCP server
CMD ["python", "mcp_server.py", "--host", "0.0.0.0", "--port", "3000"]
'''
        else:
            dockerfile_content = '''# Generic Python Application Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "main.py"]
'''
        
        return dockerfile_content
    
    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for multi-service deployment."""
        compose_content = '''version: '3.8'

services:
  # Main Streamlit Application
  streamlit-app:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./knowledge_base_pdfs:/app/knowledge_base_pdfs:ro
      - ./chroma_db:/app/chroma_db
    depends_on:
      - mcp-server
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # MCP Server
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "3000:3000"
    environment:
      - PYTHONPATH=/app
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./knowledge_base_pdfs:/app/knowledge_base_pdfs:ro
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; s=socket.socket(); s.connect(('localhost', 3000)); s.close()"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - streamlit-app
    restart: unless-stopped

  # Monitoring with Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  default:
    driver: bridge
'''
        return compose_content
    
    def generate_kubernetes_manifests(self) -> Dict[str, str]:
        """Generate Kubernetes deployment manifests."""
        manifests = {}
        
        # Namespace
        manifests['namespace.yaml'] = '''apiVersion: v1
kind: Namespace
metadata:
  name: ai-customer-service
  labels:
    app: ai-customer-service
'''
        
        # ConfigMap
        manifests['configmap.yaml'] = '''apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ai-customer-service
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  STREAMLIT_SERVER_PORT: "8501"
  MCP_SERVER_PORT: "3000"
'''
        
        # Streamlit Deployment
        manifests['streamlit-deployment.yaml'] = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: streamlit-app
  namespace: ai-customer-service
  labels:
    app: streamlit-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: streamlit-app
  template:
    metadata:
      labels:
        app: streamlit-app
    spec:
      containers:
      - name: streamlit
        image: ai-customer-service:streamlit-latest
        ports:
        - containerPort: 8501
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
      imagePullPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: streamlit-service
  namespace: ai-customer-service
spec:
  selector:
    app: streamlit-app
  ports:
  - port: 80
    targetPort: 8501
  type: ClusterIP
'''
        
        # MCP Server Deployment
        manifests['mcp-deployment.yaml'] = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: ai-customer-service
  labels:
    app: mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp
        image: ai-customer-service:mcp-latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
          limits:
            memory: "512Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-service
  namespace: ai-customer-service
spec:
  selector:
    app: mcp-server
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
'''
        
        # Ingress
        manifests['ingress.yaml'] = '''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: ai-customer-service
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: app-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: streamlit-service
            port:
              number: 80
      - path: /mcp
        pathType: Prefix
        backend:
          service:
            name: mcp-service
            port:
              number: 3000
'''
        
        return manifests
    
    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration for reverse proxy."""
        nginx_config = '''events {
    worker_connections 1024;
}

http {
    upstream streamlit_backend {
        server streamlit-app:8501;
    }
    
    upstream mcp_backend {
        server mcp-server:3000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=app:10m rate=10r/s;
    
    server {
        listen 80;
        server_name localhost;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Rate limiting
        limit_req zone=app burst=20 nodelay;
        
        # Main application
        location / {
            proxy_pass http://streamlit_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
        
        # MCP endpoints
        location /mcp {
            proxy_pass http://mcp_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
'''
        return nginx_config
    
    def generate_monitoring_config(self) -> Dict[str, str]:
        """Generate monitoring and observability configurations."""
        configs = {}
        
        # Prometheus configuration
        configs['prometheus.yml'] = '''global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'streamlit-app'
    static_configs:
      - targets: ['streamlit-app:8501']
    metrics_path: /metrics
    scrape_interval: 30s
  
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:3000']
    metrics_path: /metrics
    scrape_interval: 30s
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
  
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
'''
        
        # Alert rules
        configs['alert_rules.yml'] = '''groups:
- name: ai_app_alerts
  rules:
  - alert: HighResponseTime
    expr: avg_over_time(response_time_seconds[5m]) > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "Average response time is above 5 seconds for 2 minutes"

  - alert: HighErrorRate
    expr: rate(errors_total[5m]) > 0.1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is above 10% for 1 minute"

  - alert: ServiceDown
    expr: up == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "Service has been down for more than 30 seconds"
'''
        
        return configs
    
    def generate_ci_cd_pipeline(self) -> Dict[str, str]:
        """Generate CI/CD pipeline configurations."""
        pipelines = {}
        
        # GitHub Actions workflow
        pipelines['.github/workflows/deploy.yml'] = '''name: Deploy AI Customer Service

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: |
        pytest tests/ -v
    
    - name: Run security scan
      run: |
        pip install bandit safety
        bandit -r . -f json -o bandit-report.json || true
        safety check --json --output safety-report.json || true
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          bandit-report.json
          safety-report.json

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push Docker images
      run: |
        # Build Streamlit image
        docker build -f Dockerfile.streamlit -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:streamlit-${{ github.sha }} .
        docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:streamlit-${{ github.sha }} ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:streamlit-latest
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:streamlit-${{ github.sha }}
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:streamlit-latest
        
        # Build MCP image
        docker build -f Dockerfile.mcp -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:mcp-${{ github.sha }} .
        docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:mcp-${{ github.sha }} ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:mcp-latest
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:mcp-${{ github.sha }}
        docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:mcp-latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Add deployment commands here
    
    - name: Run smoke tests
      run: |
        echo "Running smoke tests..."
        # Add smoke test commands here
    
    - name: Deploy to production
      if: success()
      run: |
        echo "Deploying to production environment..."
        # Add production deployment commands here
'''
        
        # GitLab CI pipeline
        pipelines['.gitlab-ci.yml'] = '''stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

before_script:
  - docker info

test:
  stage: test
  image: python:3.11
  services:
    - docker:dind
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-asyncio bandit safety
    - pytest tests/ -v
    - bandit -r . -f json -o bandit-report.json
    - safety check
  artifacts:
    reports:
      junit: test-report.xml
    paths:
      - bandit-report.json

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -f Dockerfile.streamlit -t $CI_REGISTRY_IMAGE:streamlit-$CI_COMMIT_SHA .
    - docker build -f Dockerfile.mcp -t $CI_REGISTRY_IMAGE:mcp-$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:streamlit-$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:mcp-$CI_COMMIT_SHA
  only:
    - main

deploy_staging:
  stage: deploy
  script:
    - echo "Deploying to staging..."
    - kubectl apply -f k8s/
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

deploy_production:
  stage: deploy
  script:
    - echo "Deploying to production..."
    - kubectl apply -f k8s/
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
'''
        
        return pipelines

class MonitoringManager:
    """
    Production monitoring and observability manager.
    Handles metrics collection, alerting, and performance monitoring.
    """
    
    def __init__(self, app_name: str = "ai-customer-service"):
        """Initialize monitoring manager."""
        self.app_name = app_name
        self.metrics = {}
        self.alerts = []
        self.performance_data = []
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Initialize metrics
        self._initialize_metrics()
        
        logger.info(f"Monitoring manager initialized for {app_name}")
    
    def _initialize_metrics(self):
        """Initialize monitoring metrics."""
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "response_time_total": 0.0,
            "avg_response_time": 0.0,
            "active_users": 0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "database_connections": 0,
            "cache_hit_rate": 0.0,
            "errors_last_hour": 0,
            "uptime_seconds": 0
        }
    
    def record_request(self, response_time: float, success: bool = True):
        """Record a request metric."""
        self.metrics["requests_total"] += 1
        self.metrics["response_time_total"] += response_time
        
        if success:
            self.metrics["requests_successful"] += 1
        else:
            self.metrics["requests_failed"] += 1
            self.metrics["errors_last_hour"] += 1
        
        # Update average response time
        if self.metrics["requests_total"] > 0:
            self.metrics["avg_response_time"] = (
                self.metrics["response_time_total"] / self.metrics["requests_total"]
            )
        
        # Store performance data point
        data_point = {
            "timestamp": datetime.now().isoformat(),
            "response_time": response_time,
            "success": success,
            "total_requests": self.metrics["requests_total"]
        }
        self.performance_data.append(data_point)
        
        # Keep only last 1000 data points
        if len(self.performance_data) > 1000:
            self.performance_data = self.performance_data[-1000:]
    
    def update_system_metrics(self, memory_usage: float, cpu_usage: float):
        """Update system resource metrics."""
        self.metrics["memory_usage"] = memory_usage
        self.metrics["cpu_usage"] = cpu_usage
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions."""
        new_alerts = []
        
        # High response time alert
        if self.metrics["avg_response_time"] > 5.0:
            alert = {
                "type": "high_response_time",
                "severity": "warning",
                "message": f"Average response time is {self.metrics['avg_response_time']:.2f}s",
                "timestamp": datetime.now().isoformat(),
                "value": self.metrics["avg_response_time"]
            }
            new_alerts.append(alert)
        
        # High error rate alert
        error_rate = (
            self.metrics["requests_failed"] / max(self.metrics["requests_total"], 1)
        )
        if error_rate > 0.1:  # 10% error rate
            alert = {
                "type": "high_error_rate",
                "severity": "critical",
                "message": f"Error rate is {error_rate:.1%}",
                "timestamp": datetime.now().isoformat(),
                "value": error_rate
            }
            new_alerts.append(alert)
        
        # High resource usage alerts
        if self.metrics["memory_usage"] > 90.0:
            alert = {
                "type": "high_memory_usage",
                "severity": "warning",
                "message": f"Memory usage is {self.metrics['memory_usage']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "value": self.metrics["memory_usage"]
            }
            new_alerts.append(alert)
        
        if self.metrics["cpu_usage"] > 80.0:
            alert = {
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": f"CPU usage is {self.metrics['cpu_usage']:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "value": self.metrics["cpu_usage"]
            }
            new_alerts.append(alert)
        
        # Add new alerts to list
        self.alerts.extend(new_alerts)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        return new_alerts
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        error_rate = (
            self.metrics["requests_failed"] / max(self.metrics["requests_total"], 1)
        )
        
        # Determine health status
        if error_rate > 0.2 or self.metrics["avg_response_time"] > 10.0:
            status = "unhealthy"
        elif error_rate > 0.05 or self.metrics["avg_response_time"] > 5.0:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "error_rate": error_rate,
            "avg_response_time": self.metrics["avg_response_time"],
            "total_requests": self.metrics["requests_total"],
            "uptime": self.metrics["uptime_seconds"],
            "active_alerts": len([a for a in self.alerts if a["severity"] == "critical"]),
            "last_check": datetime.now().isoformat()
        }
    
    def export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        prometheus_metrics = f'''# HELP requests_total Total number of requests
# TYPE requests_total counter
requests_total {self.metrics["requests_total"]}

# HELP requests_successful_total Number of successful requests
# TYPE requests_successful_total counter
requests_successful_total {self.metrics["requests_successful"]}

# HELP requests_failed_total Number of failed requests
# TYPE requests_failed_total counter
requests_failed_total {self.metrics["requests_failed"]}

# HELP response_time_seconds Average response time in seconds
# TYPE response_time_seconds gauge
response_time_seconds {self.metrics["avg_response_time"]}

# HELP memory_usage_percent Memory usage percentage
# TYPE memory_usage_percent gauge
memory_usage_percent {self.metrics["memory_usage"]}

# HELP cpu_usage_percent CPU usage percentage
# TYPE cpu_usage_percent gauge
cpu_usage_percent {self.metrics["cpu_usage"]}

# HELP uptime_seconds Application uptime in seconds
# TYPE uptime_seconds counter
uptime_seconds {self.metrics["uptime_seconds"]}
'''
        return prometheus_metrics
    
    def start_monitoring(self):
        """Start background monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        start_time = time.time()
        
        while self.monitoring_active:
            try:
                # Update uptime
                self.metrics["uptime_seconds"] = int(time.time() - start_time)
                
                # Check alerts
                self.check_alerts()
                
                # Simulate system metrics (in real deployment, use actual system monitoring)
                import random
                self.update_system_metrics(
                    memory_usage=random.uniform(30, 70),
                    cpu_usage=random.uniform(10, 60)
                )
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error

class SecurityManager:
    """
    Production security manager for AI applications.
    Handles authentication, authorization, and security best practices.
    """
    
    def __init__(self):
        """Initialize security manager."""
        self.security_policies = {}
        self.access_logs = []
        self.security_events = []
        
        self._initialize_security_policies()
        
        logger.info("Security manager initialized")
    
    def _initialize_security_policies(self):
        """Initialize security policies."""
        self.security_policies = {
            "authentication_required": True,
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 60,
                "burst_allowance": 10
            },
            "data_encryption": {
                "at_rest": True,
                "in_transit": True,
                "algorithm": "AES-256"
            },
            "audit_logging": {
                "enabled": True,
                "retention_days": 90,
                "sensitive_data_masking": True
            },
            "api_security": {
                "cors_enabled": True,
                "csrf_protection": True,
                "content_security_policy": True
            },
            "vulnerability_scanning": {
                "enabled": True,
                "frequency": "daily"
            }
        }
    
    def generate_security_headers(self) -> Dict[str, str]:
        """Generate security headers for HTTP responses."""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
        }
    
    def mask_sensitive_data(self, data: str) -> str:
        """Mask sensitive data in logs."""
        import re
        
        # Mask email addresses
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     '***@***.***', data)
        
        # Mask credit card numbers
        data = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 
                     '****-****-****-****', data)
        
        # Mask phone numbers
        data = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 
                     '***-***-****', data)
        
        return data
    
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """Validate user input for security."""
        issues = []
        
        # Check for potential injection attacks
        injection_patterns = [
            r'<script', r'javascript:', r'onload=', r'onerror=',
            r'DROP TABLE', r'DELETE FROM', r'INSERT INTO', r'UPDATE.*SET',
            r'UNION SELECT', r'OR 1=1', r'AND 1=1'
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                issues.append(f"Potential injection detected: {pattern}")
        
        # Check input length
        if len(user_input) > 10000:
            issues.append("Input too long")
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in user_input if not c.isalnum()) / max(len(user_input), 1)
        if special_char_ratio > 0.5:
            issues.append("Excessive special characters")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "sanitized_input": self._sanitize_input(user_input)
        }
    
    def _sanitize_input(self, user_input: str) -> str:
        """Sanitize user input."""
        import html
        
        # HTML escape
        sanitized = html.escape(user_input)
        
        # Remove or escape dangerous characters
        dangerous_chars = {'<', '>', '"', "'", '&', ';', '(', ')', '{', '}'}
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, f'&#x{ord(char):02x};')
        
        return sanitized
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
            "masked_details": self.mask_sensitive_data(str(details))
        }
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        logger.warning(f"Security event: {event_type} - {event['masked_details']}")

def demo_production_deployment():
    """
    Demonstrate production deployment concepts and best practices.
    """
    print("=== Phase 3d: Deployment & Production Demo ===\n")
    
    # Initialize deployment manager
    print("🚀 Initializing Production Deployment Manager...")
    deployment = ProductionDeploymentManager("ai-customer-service")
    print("✅ Deployment manager ready")
    
    # Generate deployment configurations
    print("\n📄 Generating Deployment Configurations...")
    
    print("  • Creating Dockerfiles...")
    streamlit_dockerfile = deployment.generate_dockerfile("streamlit")
    mcp_dockerfile = deployment.generate_dockerfile("mcp-server")
    
    print("  • Creating Docker Compose configuration...")
    docker_compose = deployment.generate_docker_compose()
    
    print("  • Creating Kubernetes manifests...")
    k8s_manifests = deployment.generate_kubernetes_manifests()
    
    print("  • Creating Nginx configuration...")
    nginx_config = deployment.generate_nginx_config()
    
    print("  • Creating monitoring configurations...")
    monitoring_configs = deployment.generate_monitoring_config()
    
    print("  • Creating CI/CD pipelines...")
    ci_cd_pipelines = deployment.generate_ci_cd_pipeline()
    
    print("✅ All deployment configurations generated")
    
    # Deployment strategies
    print("\n🏗️ Deployment Strategies:")
    strategies = [
        "Blue-Green Deployment: Zero-downtime deployments with traffic switching",
        "Rolling Updates: Gradual replacement of instances",
        "Canary Deployments: Testing with small percentage of traffic",
        "A/B Testing: Comparing different versions with user segments",
        "Feature Flags: Conditional feature activation",
        "Infrastructure as Code: Reproducible infrastructure provisioning"
    ]
    
    for strategy in strategies:
        print(f"  • {strategy}")
    
    # Container orchestration
    print("\n🐳 Container Orchestration:")
    orchestration_features = [
        "Service Discovery: Automatic service location and load balancing",
        "Health Checks: Automatic restart of unhealthy containers",
        "Scaling: Horizontal and vertical scaling based on metrics",
        "Resource Management: CPU and memory allocation and limits",
        "Configuration Management: Environment variables and secrets",
        "Persistent Storage: Volume management for data persistence"
    ]
    
    for feature in orchestration_features:
        print(f"  • {feature}")
    
    # Initialize monitoring
    print("\n📊 Initializing Production Monitoring...")
    monitoring = MonitoringManager("ai-customer-service")
    monitoring.start_monitoring()
    
    # Simulate some requests for metrics
    print("  • Simulating application traffic...")
    import random
    for i in range(20):
        response_time = random.uniform(0.5, 3.0)
        success = random.random() > 0.05  # 95% success rate
        monitoring.record_request(response_time, success)
    
    # Show monitoring metrics
    print("  • Current metrics:")
    health = monitoring.get_health_status()
    for key, value in health.items():
        print(f"    - {key}: {value}")
    
    # Check for alerts
    alerts = monitoring.check_alerts()
    if alerts:
        print(f"  • Active alerts: {len(alerts)}")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"    - {alert['type']}: {alert['message']}")
    
    # Initialize security
    print("\n🔒 Initializing Security Manager...")
    security = SecurityManager()
    
    # Demonstrate security features
    print("  • Security policies:")
    for policy, config in security.security_policies.items():
        print(f"    - {policy}: {config}")
    
    print("  • Security headers:")
    headers = security.generate_security_headers()
    for header, value in headers.items():
        print(f"    - {header}: {value}")
    
    # Test input validation
    print("  • Testing input validation...")
    test_inputs = [
        "Hello, I need help with my order",
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "What is your return policy?"
    ]
    
    for test_input in test_inputs:
        validation = security.validate_input(test_input)
        status = "✅ Valid" if validation["valid"] else "❌ Invalid"
        print(f"    - \"{test_input[:30]}...\": {status}")
        if not validation["valid"]:
            print(f"      Issues: {', '.join(validation['issues'])}")
    
    # Performance optimization
    print("\n⚡ Performance Optimization Strategies:")
    optimizations = [
        "Caching: Redis for session data and frequently accessed content",
        "CDN: Content delivery network for static assets",
        "Database Optimization: Query optimization and connection pooling",
        "Load Balancing: Distribute traffic across multiple instances",
        "Async Processing: Background tasks for heavy operations",
        "Resource Compression: Gzip compression for responses",
        "Memory Management: Proper cleanup and garbage collection",
        "Connection Pooling: Reuse database and API connections"
    ]
    
    for optimization in optimizations:
        print(f"  • {optimization}")
    
    # Scaling considerations
    print("\n📈 Scaling Considerations:")
    scaling_factors = [
        "Horizontal Scaling: Add more instances based on load",
        "Vertical Scaling: Increase resources per instance",
        "Auto-scaling: Automatic scaling based on metrics",
        "Database Scaling: Read replicas and sharding",
        "Microservices: Break down monolith into smaller services",
        "Event-Driven Architecture: Decouple components with events",
        "Cost Optimization: Right-sizing and reserved instances",
        "Geographic Distribution: Multi-region deployments"
    ]
    
    for factor in scaling_factors:
        print(f"  • {factor}")
    
    # Security best practices
    print("\n🛡️ Security Best Practices:")
    security_practices = [
        "Zero Trust Architecture: Never trust, always verify",
        "Principle of Least Privilege: Minimal necessary permissions",
        "Defense in Depth: Multiple layers of security",
        "Regular Security Audits: Penetration testing and code reviews",
        "Vulnerability Management: Regular scanning and patching",
        "Incident Response: Prepared response plans and procedures",
        "Data Privacy: GDPR/CCPA compliance and data protection",
        "Secure Development: Security in the development lifecycle"
    ]
    
    for practice in security_practices:
        print(f"  • {practice}")
    
    # Cost management
    print("\n💰 Cost Management:")
    cost_strategies = [
        "Resource Right-sizing: Match resources to actual needs",
        "Reserved Instances: Long-term commitments for discounts",
        "Spot Instances: Use spare capacity for cost savings",
        "Auto-scaling: Scale down during low usage periods",
        "Storage Optimization: Archive old data to cheaper storage",
        "Network Optimization: Minimize data transfer costs",
        "Monitoring and Alerting: Track costs and set budgets",
        "Regular Cost Reviews: Analyze and optimize spending"
    ]
    
    for strategy in cost_strategies:
        print(f"  • {strategy}")
    
    # Disaster recovery
    print("\n🚨 Disaster Recovery & Business Continuity:")
    dr_components = [
        "Backup Strategy: Regular automated backups with testing",
        "Multi-region Deployment: Geographic redundancy",
        "Database Replication: Real-time data synchronization",
        "Recovery Time Objective (RTO): Target recovery time",
        "Recovery Point Objective (RPO): Acceptable data loss",
        "Failover Procedures: Automated and manual failover",
        "Communication Plan: Stakeholder notification procedures",
        "Testing: Regular disaster recovery drills"
    ]
    
    for component in dr_components:
        print(f"  • {component}")
    
    # Stop monitoring
    monitoring.stop_monitoring()
    
    print("\n🎓 Phase 3d Complete!")
    print("✅ Production deployment strategies covered")
    print("✅ Monitoring and observability implemented")
    print("✅ Security best practices applied")
    print("✅ Performance optimization strategies outlined")
    print("✅ Scaling and cost management covered")

def interactive_deployment_planning():
    """Interactive deployment planning session."""
    print("\n=== Interactive Deployment Planning ===")
    print("Let's plan your AI application deployment!\n")
    
    # Gather requirements
    print("📋 Deployment Requirements Assessment:")
    
    try:
        expected_users = input("Expected number of concurrent users (default: 100): ").strip()
        expected_users = int(expected_users) if expected_users else 100
        
        availability_target = input("Availability target (default: 99.9%): ").strip()
        availability_target = availability_target if availability_target else "99.9%"
        
        deployment_env = input("Deployment environment (cloud/on-premise/hybrid, default: cloud): ").strip()
        deployment_env = deployment_env if deployment_env else "cloud"
        
        budget_range = input("Monthly budget range (low/medium/high, default: medium): ").strip()
        budget_range = budget_range if budget_range else "medium"
        
        compliance_req = input("Compliance requirements (GDPR/HIPAA/SOC2/none, default: none): ").strip()
        compliance_req = compliance_req if compliance_req else "none"
        
    except KeyboardInterrupt:
        print("\n👋 Planning session cancelled.")
        return
    
    # Generate recommendations
    print(f"\n🎯 Deployment Recommendations for your requirements:")
    print(f"  • Expected Users: {expected_users}")
    print(f"  • Availability Target: {availability_target}")
    print(f"  • Environment: {deployment_env}")
    print(f"  • Budget: {budget_range}")
    print(f"  • Compliance: {compliance_req}")
    
    print(f"\n📊 Recommended Architecture:")
    
    # Architecture recommendations based on scale
    if expected_users < 50:
        print("  • Single-instance deployment with load balancer")
        print("  • Shared database with regular backups")
        print("  • Basic monitoring with alerting")
        print("  • Estimated cost: $200-500/month")
    elif expected_users < 500:
        print("  • Multi-instance deployment with auto-scaling")
        print("  • Database with read replicas")
        print("  • Advanced monitoring and logging")
        print("  • CDN for static content delivery")
        print("  • Estimated cost: $500-2000/month")
    else:
        print("  • Microservices architecture with Kubernetes")
        print("  • Database cluster with sharding")
        print("  • Full observability stack (metrics, logs, traces)")
        print("  • Multi-region deployment for high availability")
        print("  • Advanced security and compliance features")
        print("  • Estimated cost: $2000+/month")
    
    # Compliance recommendations
    if compliance_req.upper() in ['GDPR', 'HIPAA', 'SOC2']:
        print(f"\n🔒 {compliance_req.upper()} Compliance Requirements:")
        if compliance_req.upper() == 'GDPR':
            print("  • Data residency in EU regions")
            print("  • User consent management")
            print("  • Right to erasure implementation")
            print("  • Data processing audit logs")
        elif compliance_req.upper() == 'HIPAA':
            print("  • Encrypted data at rest and in transit")
            print("  • Access controls and audit logging")
            print("  • Business Associate Agreements")
            print("  • Regular security assessments")
        elif compliance_req.upper() == 'SOC2':
            print("  • Security controls implementation")
            print("  • Availability monitoring")
            print("  • Processing integrity checks")
            print("  • Confidentiality measures")
    
    print(f"\n🚀 Next Steps:")
    print("  1. Set up development environment")
    print("  2. Create staging environment for testing")
    print("  3. Implement monitoring and alerting")
    print("  4. Conduct security assessment")
    print("  5. Deploy to production with gradual rollout")
    print("  6. Monitor and optimize based on real usage")

if __name__ == "__main__":
    # Run production deployment demonstration
    demo_production_deployment()
    
    # Optional interactive planning
    print("\n" + "="*60)
    choice = input("Would you like to run interactive deployment planning? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_deployment_planning()
    
    print("\n🎉 AI Enterprise Accelerator Training Complete!")
    print("🏆 You've successfully learned:")
    print("  • Day 1: Models & RAG - LLM integration and retrieval systems")
    print("  • Day 2: Agents & MCP - Intelligent agents and tool protocols")  
    print("  • Day 3: Production - UI development and deployment strategies")
    print("\n🚀 Ready to build production AI applications!")