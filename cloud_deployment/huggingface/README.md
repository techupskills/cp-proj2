# HuggingFace Spaces Deployment Guide

Deploy the AI Customer Service Platform to HuggingFace Spaces for easy sharing and demonstration.

## Why HuggingFace Spaces?

- **Free hosting** for public applications
- **Zero infrastructure management** 
- **Automatic scaling** and resource management
- **Built-in community features** (likes, comments, discussions)
- **Easy sharing** with direct URL access
- **Multiple runtime options** (Streamlit, Gradio, Docker)

## Deployment Options

### 1. Streamlit Space (Recommended)
- **Best for**: Demo and showcase applications
- **Resources**: 2 vCPU, 16GB RAM, 50GB disk
- **Setup time**: 5-10 minutes
- **Cost**: Free for public spaces

### 2. Docker Space
- **Best for**: Complex applications with custom dependencies
- **Resources**: Customizable container environment
- **Setup time**: 10-15 minutes
- **Cost**: Free for public spaces, paid for private

## Prerequisites

### 1. HuggingFace Account
```bash
# Create account at https://huggingface.co
# Get your access token from https://huggingface.co/settings/tokens
```

### 2. Install HuggingFace CLI
```bash
pip install huggingface_hub
huggingface-cli login
```

### 3. Git LFS (for large files)
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pdf"
git lfs track "*.pkl"
git lfs track "*.bin"
```

## Quick Start: Streamlit Space

### Step 1: Create Space
1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **Name**: `ai-customer-service`
   - **License**: `mit` (or your preferred license)
   - **SDK**: `Streamlit`
   - **Visibility**: `Public` (for free hosting)

### Step 2: Clone and Configure
```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/ai-customer-service
cd ai-customer-service

# Copy application files
cp /path/to/your/project/*.py .
cp /path/to/your/project/requirements.txt .
cp -r /path/to/your/project/knowledge_base_pdfs/ .
```

### Step 3: Create Space Configuration
```bash
# Run the automated setup script
../scripts/setup-huggingface-space.sh
```

## Automated Deployment

Use our automated deployment script:

```bash
# Interactive deployment
./cloud_deployment/huggingface/deploy-to-huggingface.sh

# Direct deployment with parameters
./cloud_deployment/huggingface/deploy-to-huggingface.sh \
  --username YOUR_USERNAME \
  --space-name ai-customer-service \
  --sdk streamlit
```

## Manual Deployment Steps

### Step 1: Prepare Application Files

Create the necessary configuration files for HuggingFace Spaces:

#### `app.py` (Main application file)
```python
#!/usr/bin/env python3
"""
HuggingFace Spaces version of AI Customer Service Platform
Optimized for cloud deployment without local dependencies
"""

import streamlit as st
import os
import sys

# Set up the application for HuggingFace Spaces
os.environ['HUGGINGFACE_SPACES'] = 'true'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Import the main application
from streamlit_app import main

if __name__ == "__main__":
    main()
```

#### `requirements.txt` (Dependencies)
```txt
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
chromadb>=0.4.0
pypdf>=3.15.0
python-docx>=0.8.11
sentence-transformers>=2.2.2
huggingface-hub>=0.16.0
```

#### `README.md` (Space description)
```markdown
---
title: AI Customer Service Platform
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# AI Customer Service Platform

An intelligent customer service platform powered by RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol).

## Features

- 💬 Intelligent chat interface
- 📚 Knowledge base integration
- 🔍 Semantic search capabilities
- 📊 Real-time analytics
- 🎯 Agent dashboard

## Usage

1. Select between Customer View and Agent Dashboard
2. Ask questions about products, returns, shipping, etc.
3. View real-time analytics and system performance

## Technology Stack

- **Frontend**: Streamlit
- **AI**: Local LLM integration with fallback to API
- **Search**: ChromaDB vector database
- **Protocol**: Model Context Protocol (MCP)

Built for the AI Enterprise Accelerator Training Program.
```

### Step 2: Optimize for HuggingFace Spaces

#### Create `packages.txt` (System dependencies)
```txt
curl
build-essential
```

#### Create `config.toml` (Streamlit configuration)
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#1f2937"
```

### Step 3: Adapt Application for Cloud

Create `huggingface_app.py` (Modified version for Spaces):

```python
#!/usr/bin/env python3
"""
HuggingFace Spaces optimized version of AI Customer Service Platform
"""

import streamlit as st
import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

# Configure for HuggingFace Spaces
st.set_page_config(
    page_title="AI Customer Service Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Disable warnings for cleaner demo
import warnings
warnings.filterwarnings("ignore")

class HuggingFaceCustomerService:
    """
    Customer service application optimized for HuggingFace Spaces.
    Uses API fallbacks and simplified functionality for cloud deployment.
    """
    
    def __init__(self):
        self.app_name = "AI Customer Service Platform"
        self.version = "HF-Spaces-1.0"
        self.mock_data = self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock data for demonstration."""
        return {
            "customers": {
                "john.doe@email.com": {
                    "name": "John Doe",
                    "tier": "Premium",
                    "orders": 3,
                    "last_contact": "2024-12-15"
                },
                "sarah.smith@email.com": {
                    "name": "Sarah Smith", 
                    "tier": "Standard",
                    "orders": 1,
                    "last_contact": "2024-12-10"
                }
            },
            "knowledge": [
                {
                    "category": "Returns",
                    "title": "Return Policy",
                    "content": "Items can be returned within 30 days with receipt for full refund."
                },
                {
                    "category": "Shipping",
                    "title": "Shipping Information", 
                    "content": "Standard shipping takes 3-5 business days. Express available in 1-2 days."
                }
            ]
        }

def main():
    """Main HuggingFace Spaces application."""
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(90deg, #3b82f6, #1e40af); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>🤖 AI Customer Service Platform</h1>
        <p style='color: white; opacity: 0.9; margin: 0.5rem 0 0 0;'>Intelligent customer support powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize application
    app = HuggingFaceCustomerService()
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        view_mode = st.selectbox(
            "Select View",
            ["Customer Chat", "Knowledge Base", "Analytics", "About"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Demo Stats")
        st.metric("Version", app.version)
        st.metric("Customers", len(app.mock_data["customers"]))
        st.metric("Knowledge Articles", len(app.mock_data["knowledge"]))
    
    # Main content based on view mode
    if view_mode == "Customer Chat":
        render_customer_chat(app)
    elif view_mode == "Knowledge Base":
        render_knowledge_base(app)
    elif view_mode == "Analytics":
        render_analytics(app)
    else:
        render_about()

def render_customer_chat(app):
    """Render customer chat interface."""
    st.subheader("💬 Customer Support Chat")
    
    # Customer selection
    customer_email = st.selectbox(
        "Select Customer",
        list(app.mock_data["customers"].keys()) + ["New Customer"]
    )
    
    if customer_email != "New Customer":
        customer = app.mock_data["customers"][customer_email]
        st.info(f"💼 Chatting with {customer['name']} ({customer['tier']} customer)")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(1)  # Simulate processing time
                response = generate_ai_response(prompt, app.mock_data)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_ai_response(prompt: str, mock_data: Dict) -> str:
    """Generate AI response using simple keyword matching."""
    prompt_lower = prompt.lower()
    
    # Keyword-based responses
    if any(word in prompt_lower for word in ['return', 'refund']):
        return "I can help you with returns! Our return policy allows you to return items within 30 days of purchase with your receipt. Would you like me to start a return process for you?"
    
    elif any(word in prompt_lower for word in ['shipping', 'delivery']):
        return "For shipping information: Standard shipping takes 3-5 business days ($5.99), Express shipping takes 1-2 days ($15.99). Orders over $50 get free standard shipping!"
    
    elif any(word in prompt_lower for word in ['password', 'login', 'account']):
        return "For account issues, you can reset your password by clicking 'Forgot Password' on the login page. Check your email for reset instructions within 5-10 minutes."
    
    elif any(word in prompt_lower for word in ['hello', 'hi', 'help']):
        return "Hello! Welcome to our customer service. I'm here to help with any questions about orders, returns, shipping, or account issues. What can I assist you with today?"
    
    else:
        return f"Thank you for your question about '{prompt}'. I'm here to help with information about our products, orders, returns, shipping, and account management. Could you please provide more details about what you need assistance with?"

def render_knowledge_base(app):
    """Render knowledge base browser."""
    st.subheader("📚 Knowledge Base")
    
    # Search
    search_query = st.text_input("🔍 Search knowledge base", placeholder="Enter keywords...")
    
    if search_query:
        results = [
            item for item in app.mock_data["knowledge"]
            if search_query.lower() in item["title"].lower() or search_query.lower() in item["content"].lower()
        ]
        
        if results:
            st.success(f"Found {len(results)} articles matching '{search_query}'")
            for result in results:
                with st.expander(f"📄 {result['title']} ({result['category']})"):
                    st.write(result["content"])
        else:
            st.warning(f"No articles found matching '{search_query}'")
    
    # Browse by category
    st.subheader("📂 Browse by Category")
    for item in app.mock_data["knowledge"]:
        with st.expander(f"📁 {item['category']}: {item['title']}"):
            st.write(item["content"])

def render_analytics(app):
    """Render analytics dashboard."""
    st.subheader("📊 Analytics Dashboard")
    
    # Mock analytics data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Conversations", "1,234", "+12%")
    with col2:
        st.metric("Avg Response Time", "2.3s", "-0.4s")
    with col3:
        st.metric("Customer Satisfaction", "94%", "+2%")
    with col4:
        st.metric("Issues Resolved", "89%", "+5%")
    
    # Charts
    import plotly.express as px
    import pandas as pd
    
    # Sample data for charts
    df_conversations = pd.DataFrame({
        'Date': pd.date_range('2024-12-01', '2024-12-15'),
        'Conversations': [45, 52, 61, 48, 67, 71, 58, 63, 69, 74, 68, 72, 79, 81, 85]
    })
    
    fig = px.line(df_conversations, x='Date', y='Conversations', title='Daily Conversations')
    st.plotly_chart(fig, use_container_width=True)
    
    # Category breakdown
    categories = ['Returns', 'Shipping', 'Account', 'Product Info', 'Technical']
    values = [35, 25, 20, 15, 5]
    
    fig_pie = px.pie(values=values, names=categories, title='Inquiry Categories')
    st.plotly_chart(fig_pie, use_container_width=True)

def render_about():
    """Render about page."""
    st.subheader("ℹ️ About This Application")
    
    st.markdown("""
    ### 🤖 AI Customer Service Platform
    
    This is a demonstration of an intelligent customer service platform built with:
    
    - **Streamlit** for the user interface
    - **RAG (Retrieval-Augmented Generation)** for intelligent responses
    - **MCP (Model Context Protocol)** for tool integration
    - **Vector Search** for knowledge base queries
    
    ### 🌟 Features
    
    - **Intelligent Chat Interface**: AI-powered responses to customer queries
    - **Knowledge Base Integration**: Searchable help articles and policies
    - **Customer Context**: Access to customer history and preferences
    - **Real-time Analytics**: Performance metrics and conversation insights
    
    ### 🛠️ Technology Stack
    
    - Frontend: Streamlit
    - Backend: Python
    - AI: Local LLM with API fallbacks
    - Search: ChromaDB vector database
    - Deployment: HuggingFace Spaces
    
    ### 🎓 Training Program
    
    Built as part of the **AI Enterprise Accelerator Training** program, demonstrating:
    
    1. **Day 1**: LLM integration and RAG implementation
    2. **Day 2**: AI agents and MCP protocol
    3. **Day 3**: Production deployment and scaling
    
    ### 🚀 Deployment
    
    This application is deployed on HuggingFace Spaces and can also be deployed to:
    - AWS (App Runner, ECS, Lambda)
    - Google Cloud (Cloud Run, GKE)
    - Azure (Container Instances, AKS)
    - Local Docker containers
    
    ### 📝 License
    
    MIT License - Feel free to use and modify for your own projects!
    """)
    
    st.markdown("---")
    st.markdown("Built with ❤️ for the AI community")

if __name__ == "__main__":
    main()
```

### Step 4: Deploy to HuggingFace Spaces

```bash
# Add files to git
git add .
git commit -m "Initial deployment to HuggingFace Spaces"
git push

# Your space will automatically build and deploy
# Visit https://huggingface.co/spaces/YOUR_USERNAME/ai-customer-service
```

## Configuration Options

### Space Settings

You can configure your space through the HuggingFace interface:

- **Hardware**: CPU Basic (free) or upgrade to GPU
- **Visibility**: Public (free) or Private (paid)
- **Persistent Storage**: For databases and files
- **Custom Domains**: For branded access

### Environment Variables

Set these in your Space settings:

```bash
HUGGINGFACE_SPACES=true
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=7860
LOG_LEVEL=INFO
```

### Secrets Management

For API keys and sensitive data, use HuggingFace Spaces Secrets:

1. Go to your Space settings
2. Add secrets in the "Repository secrets" section
3. Access in code with `os.environ.get('SECRET_NAME')`

## Optimizations for HuggingFace Spaces

### 1. Resource Management
- Use efficient data structures
- Cache computations with `@st.cache_data`
- Lazy load large models

### 2. Performance Tips
- Minimize dependencies in `requirements.txt`
- Use smaller model versions when possible
- Implement proper error handling

### 3. User Experience
- Add loading indicators for long operations
- Provide fallback options for API failures
- Include clear usage instructions

## Troubleshooting

### Common Issues

1. **Space Won't Start**
   ```bash
   # Check logs in Space interface
   # Verify requirements.txt syntax
   # Ensure app.py exists and is valid
   ```

2. **Out of Memory**
   ```bash
   # Reduce model sizes
   # Use CPU-only versions
   # Implement memory-efficient loading
   ```

3. **Slow Performance**
   ```bash
   # Cache expensive operations
   # Use smaller datasets
   # Optimize imports
   ```

### Debug Commands

```python
# Add debug information to your app
st.sidebar.write(f"Python version: {sys.version}")
st.sidebar.write(f"Streamlit version: {st.__version__}")
st.sidebar.write(f"Available memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
```

## Advanced Features

### 1. Persistent Storage
```python
# Use HuggingFace Datasets for persistent storage
from datasets import Dataset
import pickle

# Save data
dataset = Dataset.from_dict({"data": [pickle.dumps(my_data)]})
dataset.push_to_hub("YOUR_USERNAME/my-data")

# Load data
dataset = Dataset.load_from_hub("YOUR_USERNAME/my-data")
my_data = pickle.loads(dataset[0]["data"])
```

### 2. Community Features
```python
# Add community features
st.sidebar.markdown("""
### 🤗 Community
- ⭐ Star this Space if you find it useful
- 🐛 Report issues in Discussions
- 💡 Suggest improvements
- 🔄 Duplicate to create your own version
""")
```

### 3. Analytics Integration
```python
# Track usage with HuggingFace Analytics
from huggingface_hub import HfApi

api = HfApi()
# Log usage events (if needed)
```

## Best Practices

### 1. Code Organization
- Keep `app.py` as the main entry point
- Use separate modules for different functionalities
- Include comprehensive docstrings

### 2. Documentation
- Write clear README with usage instructions
- Include screenshots and examples
- Document any API requirements

### 3. Community Engagement
- Respond to discussions and feedback
- Update regularly with improvements
- Share in relevant communities

## Migration from Other Platforms

### From Local Development
```bash
# Copy core application files
cp streamlit_app.py app.py
cp requirements.txt .
cp -r static/ .

# Adapt for cloud deployment
# Remove local dependencies
# Add fallback options
```

### From Other Cloud Providers
```bash
# HuggingFace Spaces advantages:
# - No infrastructure management
# - Built-in community features
# - Free hosting for public apps
# - Easy sharing and discovery
```

## Next Steps

After successful deployment:

1. **Share Your Space**: Get feedback from the community
2. **Monitor Usage**: Check Space analytics and logs
3. **Iterate**: Improve based on user feedback
4. **Scale**: Consider paid tiers for private or high-usage apps
5. **Integrate**: Connect with other HuggingFace tools and models

---

**Ready to deploy?** Use the automated script or follow the manual steps above to get your AI Customer Service Platform running on HuggingFace Spaces!