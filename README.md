# AI Customer Service Platform - Complete Training Application

This repository contains a complete AI-powered customer service application with comprehensive training modules, demonstrating enterprise-ready AI implementation with RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol).

## 🏗️ Project Structure

### **Core Application**
- **`streamlit_app.py`** - Main Streamlit web interface with customer and agent dashboards
- **`mcp_agent.py`** - MCP-enabled customer support agent with RAG capabilities
- **`mcp_server.py`** - MCP server providing tools and knowledge base access
- **`knowledge_service.py`** - Knowledge base processing and vector search service
- **`generate_pdfs.py`** - Utility to generate sample knowledge base documents

### **Training Curriculum** (`training_phases/`)
Complete 3-day training program with 8 phases:

#### **Day 1: Models & RAG Foundation** 
- `phase1a_basic_llm.py` - Basic LLM integration (90 min)
- `phase1b_document_processing.py` - Document processing & embeddings (90 min) 
- `phase1c_vector_database.py` - Vector database setup (90 min)
- `phase1d_basic_rag.py` - Complete RAG implementation (90 min)

#### **Day 2: AI Agents & MCP**
- `phase2a_simple_agent.py` - Agent architecture & reasoning (90 min)
- `phase2b_multi_agent.py` - Multi-agent coordination (90 min)
- `phase2c_mcp_server.py` - MCP server implementation (90 min) 
- `phase2d_mcp_client.py` - MCP client integration (90 min)

#### **Day 3: Production Application**
- `phase3a_basic_ui.py` - Basic UI framework with Streamlit (90 min)
- `phase3b_advanced_ui.py` - Advanced analytics dashboard (90 min)
- `phase3c_integration.py` - Complete system integration (90 min)
- `phase3d_deployment.py` - Production deployment strategies (90 min)

### **Knowledge Base** (`knowledge_base_pdfs/`)
Sample PDF documents for RAG demonstration:
- Account & password policies
- Payment methods information  
- Return, shipping & support policies
- Technical troubleshooting guides

### **Cloud Deployment** (`cloud_deployment/`)
Complete deployment automation for major cloud providers:
- **AWS** - App Runner, ECS, Lambda deployment scripts
- **GCP** - Cloud Run, GKE deployment automation  
- **Azure** - Container Instances, AKS deployment tools
- **Universal Script** - One-command deployment to any cloud

### **Local Deployment Configuration**
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-service orchestration  
- `k8s-deployment.yaml` - Kubernetes deployment
- `requirements.txt` - Python dependencies
- `start.sh` - Application startup script

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Ollama for local LLM
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull required model (in separate terminal)
ollama pull llama3.2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
# Option 1: Streamlit web interface
streamlit run streamlit_app.py

# Option 2: Direct Python execution  
python streamlit_app.py
```

### 4. Access the Application
- **Web Interface**: http://localhost:8501
- **Customer View**: Chat interface for customer support
- **Agent Dashboard**: RAG visualization, system monitoring, and analytics

## 🎓 Training Program

Each training phase is a standalone 90-minute module that can be run independently:

```bash
# Example: Run basic LLM training
python training_phases/phase1a_basic_llm.py

# Example: Run RAG training with interactive demos
python training_phases/phase1d_basic_rag.py

# Example: Run complete integrated platform
python training_phases/phase3c_integration.py
```

See `training_phases/README.md` for complete training curriculum details.

## 🔧 Key Features

### **RAG (Retrieval-Augmented Generation)**
- Vector database with ChromaDB
- Semantic search across knowledge base
- Context-aware response generation
- Real-time document processing

### **MCP (Model Context Protocol)**
- Standardized AI tool communication
- Server-client architecture
- Tool registration and discovery
- Production-ready protocol implementation

### **Multi-Agent Architecture**
- Specialized agents for different tasks
- Agent coordination and communication
- Memory and state management
- Workflow orchestration

### **Production Features**
- Real-time monitoring and analytics
- Customer context management
- Conversation history tracking
- Error handling and recovery
- Security and input validation

## ☁️ Cloud Deployment (One-Command)

### **Universal Cloud Deployment**
```bash
# Interactive deployment wizard (recommended)
./cloud_deployment/scripts/cloud-deploy.sh interactive

# Direct deployment to specific cloud
./cloud_deployment/scripts/cloud-deploy.sh aws     # AWS App Runner
./cloud_deployment/scripts/cloud-deploy.sh gcp     # Google Cloud Run
./cloud_deployment/scripts/cloud-deploy.sh azure   # Azure Container Instances
```

### **Cloud-Specific Deployment**
```bash
# AWS (App Runner - Serverless containers)
./cloud_deployment/aws/deploy-to-aws-apprunner.sh

# Google Cloud (Cloud Run - Auto-scaling containers)
./cloud_deployment/gcp/deploy-to-cloud-run.sh

# Azure (Container Instances - Simple containers)
./cloud_deployment/azure/deploy-to-azure-aci.sh
```

### **Prerequisites Setup**
```bash
# Install all cloud CLI tools
./cloud_deployment/scripts/setup-prerequisites.sh --all

# Check what's already installed
./cloud_deployment/scripts/setup-prerequisites.sh --check
```

## 🐳 Local Deployment Options

### **Docker**
```bash
# Build and run with Docker
docker build -t ai-customer-service .
docker run -p 8501:8501 ai-customer-service
```

### **Docker Compose**
```bash
# Multi-service deployment
docker-compose up -d
```

### **Kubernetes**
```bash
# Deploy to Kubernetes cluster
kubectl apply -f k8s-deployment.yaml
```

## 📊 Monitoring & Analytics

The application includes built-in monitoring:
- Real-time conversation analytics
- Response time tracking
- RAG performance metrics
- System health monitoring
- User interaction patterns

## 🔒 Security Features

- Input validation and sanitization
- Rate limiting and request throttling
- Secure handling of customer data
- Audit logging for compliance
- Data privacy controls

## 📚 Documentation

- **Training Manual**: `training_phases/README.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **API Documentation**: Built into each training phase
- **Architecture Overview**: Detailed in training modules

## 🤝 Contributing

When extending the training modules:
- Maintain 90-minute session structure
- Include hands-on exercises and examples
- Provide both guided demos and interactive modes
- Document learning objectives clearly
- Add comprehensive error handling

## 📁 Archive

Non-essential files have been moved to `unused_files/` to simplify the project structure while preserving them for reference.

## 🎯 Learning Outcomes

By completing this training, you will:

1. **Understand AI Fundamentals** - LLMs, embeddings, and vector search
2. **Build RAG Systems** - Complete retrieval-augmented generation pipelines  
3. **Develop AI Agents** - Intelligent systems that use tools and reason
4. **Master MCP Protocol** - Modern client-server AI communication
5. **Create Production Apps** - Deployable applications with proper UI/UX
6. **Apply Best Practices** - Performance optimization, monitoring, security

## 🚀 Ready to Deploy

This application is production-ready and includes:
- Containerized deployment
- Monitoring and logging
- Security best practices
- Scalable architecture
- Comprehensive error handling

Perfect for enterprise AI implementations and training programs!