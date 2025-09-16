# AI Enterprise Accelerator Training - Phase Implementation

This directory contains modular implementations of the customer service AI application, broken down according to the **AI Enterprise Accelerator Training** structure led by Brent Laster.

## Training Structure Overview

### **Day 1: Models & Retrieval-Augmented Generation (RAG)**
Build fluency with AI models and extending them with business data.

### **Day 2: AI Agents & Model Context Protocol (MCP)** 
Learn to build AI agents that reason, use tools, and connect to business systems.

### **Day 3: AI for Productivity & Capstone Project**
Apply AI to software development and build a complete working application.

---

## Phase 1: Day 1 - Models & RAG Foundation ✅

Each phase is a standalone 90-minute module with hands-on exercises.

### Phase 1a: Basic LLM Integration (90 min)
**File:** `phase1a_basic_llm.py`

**Learning Objectives:**
- How LLMs work: embeddings, transformers, attention
- Finding, running, and qualifying models  
- Basic prompt engineering and response handling

**Features:**
- Simple LLM client with Ollama integration
- Prompt engineering demonstrations
- Interactive mode for experimentation
- Performance tracking and analysis

**Run:** `python phase1a_basic_llm.py`

### Phase 1b: Document Processing & Embeddings (90 min)
**File:** `phase1b_document_processing.py`

**Learning Objectives:**
- Extract text from PDF, DOCX, and TXT formats
- Understanding embeddings and semantic similarity
- Processing and chunking documents for AI consumption
- Hands-on document ingestion pipeline

**Features:**
- Multi-format document processing (PDF, DOCX, TXT)
- Intelligent text cleaning and chunking
- Embedding concept demonstrations
- Processing statistics and analysis

**Run:** `python phase1b_document_processing.py`

### Phase 1c: Vector Database Setup (90 min)  
**File:** `phase1c_vector_database.py`

**Learning Objectives:**
- Understanding vector databases and embeddings storage
- Setting up ChromaDB for semantic search
- Creating collections and managing vector data
- Basic similarity search and retrieval

**Features:**
- ChromaDB integration with persistence
- Collection management and operations
- Similarity search with quality analysis
- Interactive search interface
- Performance metrics and logging

**Run:** `python phase1c_vector_database.py`

### Phase 1d: Basic RAG Implementation (90 min)
**File:** `phase1d_basic_rag.py`

**Learning Objectives:**
- Implementing the complete RAG pipeline
- Prompt engineering with retrieved context
- Evaluating RAG system performance
- Hands-on: building agentic RAG with curated datasets

**Features:**
- Complete RAG pipeline (retrieve + generate)
- Advanced prompt engineering with context
- RAG quality evaluation and metrics
- Interactive RAG system
- Performance analysis and optimization

**Run:** `python phase1d_basic_rag.py`

---

## Dependencies

Install required packages:
```bash
pip install requests chromadb pypdf python-docx
```

Ensure Ollama is running with llama3.2 model:
```bash
ollama pull llama3.2
ollama serve
```

---

## Usage Progression

**For Training Sessions:**
1. Start with Phase 1a to understand basic LLM interaction
2. Progress through 1b (document processing) and 1c (vector storage)  
3. Complete with 1d for full RAG implementation
4. Each phase builds on the previous ones

**For Development:**
- Use individual phases as building blocks
- Import classes across phases for custom implementations
- Extend functionality based on specific needs

---

## Phase 2: Day 2 - AI Agents & MCP ✅

Each phase is a standalone 90-minute module building agent and MCP capabilities.

### Phase 2a: Simple Agent Logic (90 min)
**File:** `phase2a_simple_agent.py`

**Learning Objectives:**
- Motivations and use cases for agents
- What agents are and how they work
- Chain of thought, memory, and data management
- Hands-on: creating an AI agent that leverages tools

**Features:**
- Agent architecture with reasoning and memory
- Tool registration and execution framework
- Multi-step task solving with chain of thought
- Agent performance tracking and analysis
- Interactive agent experimentation mode

**Run:** `python phase2a_simple_agent.py`

### Phase 2b: Multi-step Agent Processing (90 min)
**File:** `phase2b_multi_agent.py`

**Learning Objectives:**
- Multi-agent design patterns
- Using RAG with agents
- Creating agents to process structured business data
- Future of AI agents in enterprise workflows

**Features:**
- Multi-agent coordination and workflows
- RAG-enhanced agents with knowledge retrieval
- Agent communication and message routing
- Workflow execution and dependency management
- Enterprise agent architecture patterns

**Run:** `python phase2b_multi_agent.py`

### Phase 2c: MCP Server Implementation (90 min)
**File:** `phase2c_mcp_server.py`

**Learning Objectives:**
- What MCP is and why it matters
- MCP architecture, transports, features
- Frameworks for MCP implementation
- Building MCP servers and tools

**Features:**
- Production-ready MCP server implementation
- Customer service tools and resources
- Vector database and RAG integration
- Protocol compliance and error handling
- Resource management and statistics

**Run:** `python phase2c_mcp_server.py` or `python phase2c_mcp_server.py --mcp-server`

### Phase 2d: MCP Client Integration (90 min)
**File:** `phase2d_mcp_client.py`

**Learning Objectives:**
- Connecting to MCP servers
- Common patterns and pitfalls
- Security and MCP adoption predictions
- Leveraging public MCP servers in AI processes

**Features:**
- MCP client with multi-server support
- Agent integration with MCP capabilities
- Connection management and error handling
- Tool discovery and dynamic registration
- Interactive MCP client interface

**Run:** `python phase2d_mcp_client.py`

---

## Phase 3: Day 3 - AI for Productivity & Capstone Project ✅

Each phase is a standalone 90-minute module building complete production-ready applications.

### Phase 3a: Basic UI Framework (90 min)
**File:** `phase3a_basic_ui.py`

**Learning Objectives:**
- Designing an AI-powered application
- Choosing a model, prompts, MCP integration
- Hands-on: build the base app, MCP server, and agent
- User interface design for AI applications

**Features:**
- Streamlit-based customer service interface
- Real-time chat interface with message bubbles
- Customer context panels and information cards
- Interactive forms with validation and feedback
- System monitoring with metrics and status indicators
- Custom CSS styling and responsive design

**Run:** `streamlit run phase3a_basic_ui.py`

### Phase 3b: Advanced UI Features (90 min)
**File:** `phase3b_advanced_ui.py`

**Learning Objectives:**
- Advanced dashboard and analytics development
- Real-time data visualization and monitoring
- Performance metrics and health indicators
- Interactive charts and data exploration

**Features:**
- Advanced analytics dashboard with Plotly visualizations
- Real-time monitoring and health indicators
- Performance metrics tracking and analysis
- Interactive charts for conversation analytics
- System health monitoring and alerting
- Advanced UI patterns and components

**Run:** `streamlit run phase3b_advanced_ui.py`

### Phase 3c: Integration & RAG Enhancement (90 min)
**File:** `phase3c_integration.py`

**Learning Objectives:**
- Complete system integration patterns
- Advanced RAG features and optimization
- Multi-agent coordination and workflows
- Production-ready application architecture

**Features:**
- Complete integrated AI platform
- Advanced RAG pipeline with quality evaluation
- Multi-agent coordination and communication
- Real-time analytics and performance monitoring
- Comprehensive error handling and recovery
- Production deployment preparation

**Run:** `python phase3c_integration.py` or `streamlit run phase3c_integration.py`

### Phase 3d: Deployment & Production (90 min)
**File:** `phase3d_deployment.py`

**Learning Objectives:**
- Production deployment strategies for AI applications
- Container orchestration and scaling considerations
- Monitoring, logging, and observability patterns
- Security, authentication, and data privacy
- Performance optimization and cost management
- CI/CD pipelines for AI applications

**Features:**
- Production deployment manager with Docker/Kubernetes
- Comprehensive monitoring and alerting system
- Security manager with input validation and audit logging
- CI/CD pipeline configurations (GitHub Actions, GitLab CI)
- Container orchestration manifests and configurations
- Interactive deployment planning tool

**Run:** `python phase3d_deployment.py`

---

## Key Learning Outcomes

By completing these phases, participants will:

1. **Understand AI Fundamentals** - Core concepts of LLMs, embeddings, and vector search
2. **Build RAG Systems** - Complete retrieval-augmented generation pipelines
3. **Develop AI Agents** - Intelligent systems that use tools and reason
4. **Master MCP Protocol** - Modern client-server AI communication
5. **Create Production Apps** - Deployable AI applications with proper UI/UX
6. **Apply Best Practices** - Performance optimization, error handling, monitoring

---

## Contributing

When extending these modules:
- Maintain the 90-minute session structure
- Include hands-on exercises and examples
- Provide both guided demos and interactive modes
- Document learning objectives clearly
- Add comprehensive error handling and logging

---

## Support

Each phase includes:
- Detailed docstrings and comments
- Error handling and troubleshooting
- Performance metrics and logging
- Interactive demonstration modes
- Extensible architecture for customization