# =============================================================================
# DEPLOYMENT FILES - Add these to your project bundle
# =============================================================================

# =============================================================================
# FILE: deploy.py
# Deployment script for multiple cloud platforms
# =============================================================================
cat > deploy.py << 'EOF'
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
EOF

# =============================================================================
# FILE: sample_data.py
# Sample data for demos and testing
# =============================================================================
cat > sample_data.py << 'EOF'
"""
Sample data for Customer Support AI Agent demo
This file contains the sample knowledge base and customer data used in the demo
"""

# Company knowledge base documents
KNOWLEDGE_BASE_DOCS = [
    {
        "id": "policy_returns",
        "title": "Return Policy",
        "content": "Our return policy allows returns within 30 days of purchase with original receipt. Items must be in original condition and packaging. Refunds processed within 5-7 business days.",
        "category": "returns",
        "last_updated": "2024-11-01"
    },
    {
        "id": "policy_shipping", 
        "title": "Shipping Information",
        "content": "Standard shipping takes 3-5 business days within the US. Express shipping (1-2 days) available for additional $15 fee. International shipping available to most countries, 7-14 days.",
        "category": "shipping",
        "last_updated": "2024-11-15"
    },
    {
        "id": "policy_support",
        "title": "Support Hours", 
        "content": "Technical support available Monday-Friday 9AM-6PM EST. Premium customers get 24/7 support access via priority line. Live chat available during business hours.",
        "category": "support",
        "last_updated": "2024-10-15"
    },
    {
        "id": "troubleshoot_power",
        "title": "Device Won't Turn On",
        "content": "If device won't turn on: 1) Check power cable is securely connected 2) Try different power outlet 3) Hold power button for 10 seconds to hard reset 4) Check battery indicator if applicable",
        "category": "troubleshooting",
        "last_updated": "2024-11-20"
    },
    {
        "id": "account_password",
        "title": "Password Reset",
        "content": "To reset password: visit login page, click 'Forgot Password', enter email address, check email for reset link (may take 5-10 minutes), follow instructions in email.",
        "category": "account",
        "last_updated": "2024-10-30"
    },
    {
        "id": "warranty_info",
        "title": "Warranty Coverage",
        "content": "All products include 1-year manufacturer warranty covering defects. Extended warranty available for purchase. Warranty does not cover physical damage or normal wear.",
        "category": "warranty", 
        "last_updated": "2024-09-15"
    },
    {
        "id": "payment_methods",
        "title": "Accepted Payment Methods",
        "content": "We accept Visa, MasterCard, American Express, Discover, PayPal, Apple Pay, and Google Pay. Payment is processed securely at checkout.",
        "category": "payment",
        "last_updated": "2024-11-01"
    }
]

# Sample customer database
CUSTOMER_DATABASE = {
    "john.doe@email.com": {
        "customer_id": "CUST-001",
        "name": "John Doe",
        "tier": "Premium",
        "join_date": "2023-05-15",
        "phone": "+1-555-0123",
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY", 
            "zip": "10001"
        },
        "orders": [
            {
                "id": "ORD-001", 
                "date": "2024-11-15", 
                "product": "Wireless Headphones Pro",
                "price": 299.99,
                "status": "Delivered",
                "tracking": "1Z999AA1234567890"
            },
            {
                "id": "ORD-002", 
                "date": "2024-12-01", 
                "product": "Bluetooth Speaker Max", 
                "price": 199.99,
                "status": "Shipped",
                "tracking": "1Z999AA1234567891"
            }
        ],
        "support_tickets": [
            {
                "id": "TKT-001",
                "date": "2024-11-20",
                "issue": "Headphones audio cutting out",
                "status": "Resolved",
                "resolution": "Replaced under warranty"
            }
        ],
        "preferences": {
            "communication": "email",
            "shipping": "express",
            "notifications": True
        }
    },
    "sarah.smith@email.com": {
        "customer_id": "CUST-002", 
        "name": "Sarah Smith",
        "tier": "Standard",
        "join_date": "2024-08-22",
        "phone": "+1-555-0456",
        "address": {
            "street": "456 Oak Ave",
            "city": "Los Angeles", 
            "state": "CA",
            "zip": "90210"
        },
        "orders": [
            {
                "id": "ORD-003",
                "date": "2024-11-20", 
                "product": "USB-C Cable 6ft",
                "price": 19.99,
                "status": "Delivered",
                "tracking": "1Z999AA1234567892"
            }
        ],
        "support_tickets": [],
        "preferences": {
            "communication": "sms",
            "shipping": "standard", 
            "notifications": False
        }
    },
    "mike.johnson@email.com": {
        "customer_id": "CUST-003",
        "name": "Mike Johnson", 
        "tier": "Premium",
        "join_date": "2022-12-03",
        "phone": "+1-555-0789",
        "address": {
            "street": "789 Pine St",
            "city": "Chicago",
            "state": "IL",
            "zip": "60601"
        },
        "orders": [
            {
                "id": "ORD-004",
                "date": "2024-10-15",
                "product": "Laptop Stand Pro",
                "price": 89.99, 
                "status": "Delivered",
                "tracking": "1Z999AA1234567893"
            },
            {
                "id": "ORD-005",
                "date": "2024-11-28",
                "product": "Wireless Mouse",
                "price": 49.99,
                "status": "Processing", 
                "tracking": "TBD"
            }
        ],
        "support_tickets": [
            {
                "id": "TKT-002",
                "date": "2024-10-20", 
                "issue": "Laptop stand wobbly",
                "status": "Open",
                "resolution": "Replacement being shipped"
            }
        ],
        "preferences": {
            "communication": "phone",
            "shipping": "express",
            "notifications": True
        }
    }
}

# Sample support tickets for demo
SAMPLE_TICKETS = [
    {
        "id": "TKT-20241201-0001",
        "customer": "john.doe@email.com", 
        "type": "Product Issue",
        "priority": "Medium",
        "status": "Open",
        "created": "2024-12-01T10:30:00",
        "description": "Bluetooth speaker not connecting to iPhone",
        "agent_notes": "Customer reports pairing issues. Troubleshooting steps provided."
    },
    {
        "id": "TKT-20241201-0002",
        "customer": "sarah.smith@email.com",
        "type": "Shipping Inquiry", 
        "priority": "Low",
        "status": "Resolved",
        "created": "2024-12-01T14:15:00",
        "description": "Question about delivery timeframe",
        "agent_notes": "Provided tracking information and delivery estimate."
    }
]

def get_sample_questions():
    """Return sample customer questions for testing"""
    return [
        "How do I return an item I bought last week?",
        "When will my order ORD-002 arrive?",
        "My wireless headphones won't turn on, can you help?", 
        "I forgot my account password, how do I reset it?",
        "What are your shipping options and costs?",
        "Can I change the shipping address on my recent order?",
        "Do you offer extended warranty on electronics?",
        "What payment methods do you accept?",
        "How do I contact technical support?",
        "My device is still under warranty but not working properly"
    ]

def get_demo_scenarios():
    """Return structured demo scenarios for presentations"""
    return [
        {
            "scenario": "Return Request",
            "customer": "john.doe@email.com",
            "question": "I want to return the headphones I bought 2 weeks ago",
            "expected_outcome": "Should reference 30-day policy and customer's order history"
        },
        {
            "scenario": "Order Tracking", 
            "customer": "john.doe@email.com",
            "question": "Where is my Bluetooth speaker order?",
            "expected_outcome": "Should find ORD-002 and provide tracking information"
        },
        {
            "scenario": "Technical Support",
            "customer": "sarah.smith@email.com", 
            "question": "My device won't charge, what should I do?",
            "expected_outcome": "Should provide troubleshooting steps and offer escalation"
        },
        {
            "scenario": "New Customer",
            "customer": "new.customer@email.com",
            "question": "What's your return policy?", 
            "expected_outcome": "Should provide policy info but note no customer history"
        }
    ]
EOF

# =============================================================================
# FILE: test_suite.py
# Comprehensive testing suite
# =============================================================================
cat > test_suite.py << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive test suite for Customer Support AI Agent
Run this to verify all components are working correctly
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Import our modules
try:
    from customer_support_agent import CustomerSupportAgent
    from sample_data import get_sample_questions, get_demo_scenarios
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    print("Make sure all required files are in the same directory")
    sys.exit(1)

class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.agent = None
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        if success:
            print(f"SUCCESS: {test_name}")
            self.passed += 1
        else:
            print(f"ERROR: {test_name}: {message}")
            self.failed += 1
    
    def test_ollama_connection(self):
        """Test Ollama service connection"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            success = response.status_code == 200
            
            if success:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                message = f"Available models: {model_names}"
            else:
                message = f"HTTP {response.status_code}"
                
            self.log_test("Ollama Connection", success, message)
            return success
            
        except requests.exceptions.ConnectionError:
            self.log_test("Ollama Connection", False, "Connection refused - is Ollama running?")
            return False
        except Exception as e:
            self.log_test("Ollama Connection", False, str(e))
            return False
    
    def test_model_response(self):
        """Test basic model functionality"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": "Say exactly: 'Model test successful'",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').lower()
                success = 'successful' in response_text
                message = f"Response: '{result.get('response', 'No response')[:50]}...'"
            else:
                success = False
                message = f"HTTP {response.status_code}"
            
            self.log_test("Model Response", success, message)
            return success
            
        except Exception as e:
            self.log_test("Model Response", False, str(e))
            return False
    
    def test_json_formatting(self):
        """Test model's ability to produce valid JSON"""
        try:
            prompt = '''Respond with valid JSON containing:
- "test": "json_formatting"
- "status": "success"
- "timestamp": current time

JSON Response:'''
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                
                try:
                    parsed = json.loads(ai_response)
                    success = parsed.get('test') == 'json_formatting'
                    message = f"Parsed: {parsed}"
                except json.JSONDecodeError:
                    success = False
                    message = f"Invalid JSON: {ai_response[:100]}"
            else:
                success = False
                message = f"HTTP {response.status_code}"
            
            self.log_test("JSON Formatting", success, message)
            return success
            
        except Exception as e:
            self.log_test("JSON Formatting", False, str(e))
            return False
    
    def test_agent_initialization(self):
        """Test CustomerSupportAgent initialization"""
        try:
            self.agent = CustomerSupportAgent()
            success = self.agent is not None
            message = "Agent initialized successfully"
            
            self.log_test("Agent Initialization", success, message)
            return success
            
        except Exception as e:
            self.log_test("Agent Initialization", False, str(e))
            return False
    
    def test_knowledge_base(self):
        """Test RAG knowledge base functionality"""
        if not self.agent:
            self.log_test("Knowledge Base", False, "Agent not initialized")
            return False
        
        try:
            # Test knowledge base search
            results = self.agent.search_knowledge_base("return policy")
            success = len(results) > 0 and any('return' in doc['content'].lower() for doc in results)
            message = f"Found {len(results)} relevant documents"
            
            self.log_test("Knowledge Base Search", success, message)
            return success
            
        except Exception as e:
            self.log_test("Knowledge Base Search", False, str(e))
            return False
    
    def test_customer_lookup(self):
        """Test customer database functionality"""
        if not self.agent:
            self.log_test("Customer Lookup", False, "Agent not initialized")
            return False
        
        try:
            # Test customer lookup
            customer = self.agent.lookup_customer("john.doe@email.com")
            success = customer is not None and customer.get('name') == 'John Doe'
            message = f"Found customer: {customer.get('name') if customer else 'None'}"
            
            self.log_test("Customer Lookup", success, message)
            return success
            
        except Exception as e:
            self.log_test("Customer Lookup", False, str(e))
            return False
    
    def test_ticket_creation(self):
        """Test support ticket creation"""
        if not self.agent:
            self.log_test("Ticket Creation", False, "Agent not initialized")
            return False
        
        try:
            # Test ticket creation
            ticket = self.agent.create_ticket(
                "test@email.com", 
                "Test Issue", 
                "This is a test ticket"
            )
            success = ticket is not None and 'id' in ticket
            message = f"Created ticket: {ticket.get('id') if ticket else 'None'}"
            
            self.log_test("Ticket Creation", success, message)
            return success
            
        except Exception as e:
            self.log_test("Ticket Creation", False, str(e))
            return False
    
    def test_end_to_end_inquiry(self):
        """Test complete customer inquiry processing"""
        if not self.agent:
            self.log_test("End-to-End Processing", False, "Agent not initialized")
            return False
        
        try:
            # Test complete inquiry processing
            inquiry = "How do I return an item?"
            customer_email = "john.doe@email.com"
            
            result = self.agent.process_customer_inquiry(customer_email, inquiry)
            
            success = (
                isinstance(result, dict) and
                'response' in result and
                'confidence' in result and
                len(result['response']) > 10
            )
            
            message = f"Response length: {len(result.get('response', ''))}"
            
            self.log_test("End-to-End Processing", success, message)
            return success
            
        except Exception as e:
            self.log_test("End-to-End Processing", False, str(e))
            return False
    
    def test_sample_scenarios(self):
        """Test all demo scenarios"""
        if not self.agent:
            self.log_test("Demo Scenarios", False, "Agent not initialized")
            return False
        
        try:
            scenarios = get_demo_scenarios()
            successful_scenarios = 0
            
            for scenario in scenarios:
                try:
                    result = self.agent.process_customer_inquiry(
                        scenario['customer'], 
                        scenario['question']
                    )
                    
                    if isinstance(result, dict) and 'response' in result:
                        successful_scenarios += 1
                        
                except Exception:
                    pass
            
            success = successful_scenarios == len(scenarios)
            message = f"{successful_scenarios}/{len(scenarios)} scenarios passed"
            
            self.log_test("Demo Scenarios", success, message)
            return success
            
        except Exception as e:
            self.log_test("Demo Scenarios", False, str(e))
            return False
    
    def test_performance(self):
        """Test response time performance"""
        if not self.agent:
            self.log_test("Performance Test", False, "Agent not initialized")
            return False
        
        try:
            start_time = time.time()
            
            result = self.agent.process_customer_inquiry(
                "john.doe@email.com",
                "What are your business hours?"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response_time < 10  # Should respond within 10 seconds
            message = f"Response time: {response_time:.2f} seconds"
            
            self.log_test("Performance Test", success, message)
            return success
            
        except Exception as e:
            self.log_test("Performance Test", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("Customer Support AI Agent - Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Define test sequence
        tests = [
            ("Ollama Connection", self.test_ollama_connection),
            ("Model Response", self.test_model_response),
            ("JSON Formatting", self.test_json_formatting),
            ("Agent Initialization", self.test_agent_initialization),
            ("Knowledge Base", self.test_knowledge_base),
            ("Customer Lookup", self.test_customer_lookup),
            ("Ticket Creation", self.test_ticket_creation),
            ("End-to-End Processing", self.test_end_to_end_inquiry),
            ("Demo Scenarios", self.test_sample_scenarios),
            ("Performance", self.test_performance),
        ]
        
        # Run tests
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            test_func()
            print()
        
        # Summary
        total_tests = len(tests)
        print("=" * 60)
        print(f"Test Results: {self.passed}/{total_tests} tests passed")
        
        if self.passed == total_tests:
            print("SUCCESS: All tests passed! System is ready for demo.")
            print("\\nYou can now run:")
            print("   streamlit run streamlit_app.py")
            
        elif self.passed > total_tests // 2:
            print("WARNING: Most tests passed, but some issues detected.")
            print("\\nCheck the failed tests above and:")
            print("   - Ensure Ollama is running: ollama serve")
            print("   - Verify model is installed: ollama pull llama3.2")
            print("   - Check all dependencies: pip install -r requirements.txt")
            
        else:
            print("ERROR: Multiple test failures detected.")
            print("\\nSetup help:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Start service: ollama serve")
            print("   3. Install model: ollama pull llama3.2")
            print("   4. Install dependencies: pip install -r requirements.txt")
            print("   5. Run tests again: python test_suite.py")
        
        return self.passed == total_tests

def main():
    """Main test function"""
    suite = TestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
EOF

# =============================================================================
# DOCKER DEPLOYMENT FILES
# =============================================================================

# FILE: Dockerfile (created by deploy.py, but here for reference)
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
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
EOF

# FILE: start.sh (startup script for Docker)
cat > start.sh << 'EOF'
#!/bin/bash

# Start Ollama in background
ollama serve &

# Wait for Ollama to start
sleep 10

# Pull the model
ollama pull llama3.2

# Start Streamlit app
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
EOF

# FILE: docker-compose.yml
cat > docker-compose.yml << 'EOF'
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
EOF

# =============================================================================
# CLOUD DEPLOYMENT CONFIGS
# =============================================================================

# FILE: Procfile (for Heroku)
cat > Procfile << 'EOF'
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
EOF

# FILE: runtime.txt (for Heroku)
cat > runtime.txt << 'EOF'
python-3.11.6
EOF

# FILE: app.yaml (for Google Cloud App Engine)
cat > app.yaml << 'EOF'
runtime: python311

env_variables:
  OLLAMA_HOST: "0.0.0.0"

automatic_scaling:
  min_instances: 1
  max_instances: 10

resources:
  cpu: 2
  memory_gb: 4
EOF

# FILE: task-definition.json (for AWS ECS)
cat > task-definition.json << 'EOF'
{
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
EOF

# =============================================================================
# KUBERNETES DEPLOYMENT
# =============================================================================

# FILE: k8s-deployment.yaml
cat > k8s-deployment.yaml << 'EOF'
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
EOF

# =============================================================================
# MONITORING AND HEALTH CHECKS
# =============================================================================

# FILE: health_check.py
cat > health_check.py << 'EOF'
import streamlit as st
import requests
import json
from datetime import datetime

def check_ollama():
    """Check Ollama service health"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return {
                "status": "healthy",
                "models": [m['name'] for m in models],
                "model_count": len(models)
            }
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def check_agent():
    """Check AI agent functionality"""
    try:
        from customer_support_agent import CustomerSupportAgent
        agent = CustomerSupportAgent()
        
        # Quick test
        result = agent.process_customer_inquiry(
            "test@example.com",
            "Health check test"
        )
        
        if isinstance(result, dict) and 'response' in result:
            return {"status": "healthy", "agent": "functional"}
        else:
            return {"status": "unhealthy", "agent": "non-functional"}
            
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def main():
    st.title("System Health Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ollama Service")
        ollama_health = check_ollama()
        
        if ollama_health['status'] == 'healthy':
            st.success("Ollama is running")
            st.write(f"Models: {ollama_health.get('model_count', 0)}")
        else:
            st.error("Ollama is not running")
            st.write(f"Error: {ollama_health.get('error', 'Unknown')}")
    
    with col2:
        st.subheader("AI Agent")
        agent_health = check_agent()
        
        if agent_health['status'] == 'healthy':
            st.success("AI Agent is functional")
        else:
            st.error("AI Agent has issues")
            st.write(f"Error: {agent_health.get('error', 'Unknown')}")
    
    # Overall status
    st.subheader("Overall Status")
    overall_healthy = (
        ollama_health['status'] == 'healthy' and 
        agent_health['status'] == 'healthy'
    )
    
    if overall_healthy:
        st.success("All systems operational")
    else:
        st.error("System issues detected")
    
    # System info
    st.subheader("System Information")
    st.json({
        "timestamp": datetime.now().isoformat(),
        "ollama": ollama_health,
        "agent": agent_health,
        "overall_status": "healthy" if overall_healthy else "unhealthy"
    })

if __name__ == "__main__":
    main()
EOF

# =============================================================================
# DEPLOYMENT GUIDE
# =============================================================================

# FILE: DEPLOYMENT.md
cat > DEPLOYMENT.md << 'EOF'
# Deployment Guide - Customer Support AI Agent

This guide covers deploying the AI Customer Support Agent to various platforms.

## Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve &
ollama pull llama3.2

# Run application
streamlit run streamlit_app.py
```

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t customer-support-ai .

# Run container
docker run -p 8501:8501 -p 11434:11434 customer-support-ai

# Or use docker-compose
docker-compose up
```

### Key Points:
- Container includes both Ollama and Streamlit
- Ports 8501 (Streamlit) and 11434 (Ollama) exposed
- Model downloaded on first startup (may take 5-10 minutes)

## Cloud Deployments

### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main
```

**Note**: Heroku has limitations with large models. Consider using smaller models like `llama3.2:1b`.

### AWS ECS
1. Build and push Docker image to ECR
2. Create ECS cluster
3. Register task definition (use `task-definition.json`)
4. Create ECS service

### Google Cloud App Engine
```bash
# Deploy using app.yaml
gcloud app deploy
```

### Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## Monitoring

### Health Checks
- Health check endpoint: `/health_check.py`
- Monitors Ollama service and AI agent functionality
- Returns JSON status for automated monitoring

### Logs
- Streamlit logs: Application events and user interactions
- Ollama logs: Model loading and inference
- Container logs: System-level events

## Performance Considerations

### Resource Requirements:
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 5GB for llama3.2 model

### Scaling:
- **Horizontal**: Multiple container instances with load balancer
- **Vertical**: Increase container resources for better performance
- **Model Selection**: Use smaller models (llama3.2:1b) for faster responses

## Security

### Best Practices:
- Use environment variables for configuration
- Enable HTTPS in production
- Implement authentication for production deployments
- Regular security updates for base images

### Network Security:
- Restrict Ollama port (11434) to internal traffic only
- Use reverse proxy for SSL termination
- Implement rate limiting

## Troubleshooting

### Common Issues:

**Container won't start:**
- Check available memory (needs 4GB minimum)
- Verify Docker has sufficient resources allocated

**Model download fails:**
- Increase container startup timeout
- Check internet connectivity
- Try smaller model variant

**Slow responses:**
- Monitor CPU/memory usage
- Consider model optimization
- Implement response caching

**Connection errors:**
- Verify Ollama service is running
- Check port forwarding configuration
- Test with health check endpoint

## Production Checklist

- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Monitoring and logging set up
- [ ] Backup and recovery procedures
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Documentation updated

## Support

For deployment issues:
1. Check logs for error details
2. Run health check endpoint
3. Verify system requirements
4. Test with minimal configuration

For the full AI Enterprise Accelerator Training program, participants learn to deploy these systems in production environments with enterprise-grade security and monitoring.
EOF

echo "Deployment files created successfully!"
echo ""
echo "Files included:"
echo "- deploy.py (interactive deployment script)"
echo "- sample_data.py (demo data and scenarios)"
echo "- test_suite.py (comprehensive testing)"
echo "- Dockerfile, docker-compose.yml (containerization)"
echo "- Procfile, runtime.txt (Heroku deployment)"
echo "- app.yaml (Google Cloud App Engine)"
echo "- task-definition.json (AWS ECS)"
echo "- k8s-deployment.yaml (Kubernetes)"
echo "- health_check.py (monitoring)"
echo "- DEPLOYMENT.md (deployment guide)"
echo ""
echo "Usage:"
echo "1. Run 'python deploy.py' for interactive deployment"
echo "2. Use specific config files for your target platform"
echo "3. Check DEPLOYMENT.md for detailed instructions"