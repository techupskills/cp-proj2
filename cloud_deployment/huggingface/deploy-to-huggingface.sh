#!/bin/bash

# HuggingFace Spaces Deployment Script for AI Customer Service Platform
# This script automates the deployment to HuggingFace Spaces

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SPACE_NAME=""
USERNAME=""
SDK="streamlit"
VISIBILITY="public"
LICENSE="mit"

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    HuggingFace Spaces Deployment                            ║"
    echo "║                   AI Customer Service Platform                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --username USERNAME     HuggingFace username (required)"
    echo "  --space-name NAME       Space name (default: ai-customer-service)"
    echo "  --sdk SDK              SDK type: streamlit, gradio, docker (default: streamlit)"
    echo "  --visibility VIS       Visibility: public, private (default: public)"
    echo "  --license LICENSE      License: mit, apache-2.0, etc. (default: mit)"
    echo "  --interactive          Interactive mode for configuration"
    echo "  --help, -h             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --interactive                              Interactive deployment"
    echo "  $0 --username myuser --space-name my-ai-app  Direct deployment"
    echo ""
}

check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check if huggingface-cli is installed
    if ! command -v huggingface-cli &> /dev/null; then
        echo -e "${RED}❌ huggingface-cli not found${NC}"
        echo "Install with: pip install huggingface_hub"
        exit 1
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git not found${NC}"
        echo "Please install Git first"
        exit 1
    fi
    
    # Check if user is logged in to HuggingFace
    if ! huggingface-cli whoami &> /dev/null; then
        echo -e "${RED}❌ Not logged in to HuggingFace${NC}"
        echo "Please run: huggingface-cli login"
        exit 1
    fi
    
    # Check if git lfs is available
    if ! command -v git-lfs &> /dev/null; then
        echo -e "${YELLOW}⚠️ Git LFS not found. Large files may not upload properly${NC}"
        echo "Install with: git lfs install"
    fi
    
    echo -e "${GREEN}✅ Prerequisites check completed${NC}"
}

interactive_setup() {
    echo -e "${BLUE}🎯 Interactive HuggingFace Spaces Setup${NC}"
    echo "=================================================="
    
    # Get HuggingFace username
    CURRENT_USER=$(huggingface-cli whoami 2>/dev/null | head -n 1 || echo "")
    if [ ! -z "$CURRENT_USER" ]; then
        read -p "HuggingFace username [$CURRENT_USER]: " input_username
        USERNAME=${input_username:-$CURRENT_USER}
    else
        read -p "HuggingFace username: " USERNAME
    fi
    
    # Get space name
    read -p "Space name [ai-customer-service]: " input_space_name
    SPACE_NAME=${input_space_name:-ai-customer-service}
    
    # Choose SDK
    echo ""
    echo "Select SDK:"
    echo "1) Streamlit (Recommended - Web app framework)"
    echo "2) Gradio (ML-focused interface)"
    echo "3) Docker (Custom container)"
    echo ""
    
    while true; do
        read -p "Enter choice (1-3): " sdk_choice
        case $sdk_choice in
            1)
                SDK="streamlit"
                break
                ;;
            2)
                SDK="gradio"
                break
                ;;
            3)
                SDK="docker"
                break
                ;;
            *)
                echo "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
    
    # Choose visibility
    echo ""
    echo "Select visibility:"
    echo "1) Public (Free hosting, visible to everyone)"
    echo "2) Private (Paid hosting, only you can see)"
    echo ""
    
    while true; do
        read -p "Enter choice (1-2): " vis_choice
        case $vis_choice in
            1)
                VISIBILITY="public"
                break
                ;;
            2)
                VISIBILITY="private"
                break
                ;;
            *)
                echo "Invalid choice. Please enter 1 or 2."
                ;;
        esac
    done
    
    # Choose license
    echo ""
    echo "Select license:"
    echo "1) MIT (Permissive, allows commercial use)"
    echo "2) Apache 2.0 (Permissive with patent protection)"
    echo "3) GPL v3 (Copyleft, must share modifications)"
    echo "4) Custom"
    echo ""
    
    while true; do
        read -p "Enter choice (1-4): " license_choice
        case $license_choice in
            1)
                LICENSE="mit"
                break
                ;;
            2)
                LICENSE="apache-2.0"
                break
                ;;
            3)
                LICENSE="gpl-3.0"
                break
                ;;
            4)
                read -p "Enter license identifier: " LICENSE
                break
                ;;
            *)
                echo "Invalid choice. Please enter 1-4."
                ;;
        esac
    done
    
    # Confirm settings
    echo ""
    echo -e "${YELLOW}📋 Deployment Summary:${NC}"
    echo "  Username: ${USERNAME}"
    echo "  Space Name: ${SPACE_NAME}"
    echo "  SDK: ${SDK}"
    echo "  Visibility: ${VISIBILITY}"
    echo "  License: ${LICENSE}"
    echo "  URL: https://huggingface.co/spaces/${USERNAME}/${SPACE_NAME}"
    echo ""
    
    read -p "Proceed with deployment? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
}

create_huggingface_files() {
    echo -e "${YELLOW}📄 Creating HuggingFace Spaces configuration files...${NC}"
    
    local temp_dir="/tmp/hf-space-${SPACE_NAME}"
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    
    # Create app.py (main entry point)
    cat > "$temp_dir/app.py" << 'EOF'
#!/usr/bin/env python3
"""
HuggingFace Spaces version of AI Customer Service Platform
Optimized for cloud deployment without local dependencies
"""

import streamlit as st
import os
import sys
import warnings

# Configure for HuggingFace Spaces
os.environ['HUGGINGFACE_SPACES'] = 'true'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Disable warnings for cleaner demo
warnings.filterwarnings("ignore")

# Set up page config
st.set_page_config(
    page_title="AI Customer Service Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import and run the main application
try:
    from streamlit_app import main
    if __name__ == "__main__":
        main()
except ImportError:
    # Fallback if streamlit_app.py is not available
    st.title("🤖 AI Customer Service Platform")
    st.error("Application modules not found. Please check the deployment.")
    st.info("This is a placeholder. The full application will be available once properly deployed.")
EOF
    
    # Create requirements.txt
    cat > "$temp_dir/requirements.txt" << 'EOF'
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
EOF
    
    # Create README.md with YAML frontmatter
    cat > "$temp_dir/README.md" << EOF
---
title: AI Customer Service Platform
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: ${SDK}
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: ${LICENSE}
---

# AI Customer Service Platform 🤖

An intelligent customer service platform powered by RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol).

## 🌟 Features

- 💬 **Intelligent Chat Interface**: AI-powered responses to customer queries
- 📚 **Knowledge Base Integration**: Searchable help articles and policies  
- 👤 **Customer Context**: Access to customer history and preferences
- 📊 **Real-time Analytics**: Performance metrics and conversation insights
- 🎯 **Agent Dashboard**: Comprehensive management interface

## 🚀 How to Use

1. **Customer Chat**: Select "Customer Chat" to interact with the AI assistant
2. **Knowledge Base**: Browse and search through help articles
3. **Analytics**: View conversation metrics and system performance
4. **About**: Learn more about the technology and implementation

## 🛠️ Technology Stack

- **Frontend**: Streamlit for interactive web interface
- **AI**: Large Language Model integration with RAG capabilities
- **Search**: ChromaDB vector database for semantic search
- **Protocol**: Model Context Protocol (MCP) for tool integration
- **Deployment**: HuggingFace Spaces for easy sharing

## 🎓 Training Program

Built as part of the **AI Enterprise Accelerator Training** program:

- **Day 1**: LLM integration and RAG implementation
- **Day 2**: AI agents and MCP protocol  
- **Day 3**: Production deployment and scaling

## 📝 License

${LICENSE} License - Feel free to use and modify for your own projects!

## 🤗 Community

- ⭐ Star this Space if you find it useful
- 🐛 Report issues in the Community tab
- 💡 Suggest improvements and new features
- 🔄 Duplicate this Space to create your own version

---

Built with ❤️ for the AI community using HuggingFace Spaces
EOF
    
    # Create .gitignore
    cat > "$temp_dir/.gitignore" << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.log
.env
.venv
temp/
.DS_Store
EOF
    
    # Create Streamlit config
    mkdir -p "$temp_dir/.streamlit"
    cat > "$temp_dir/.streamlit/config.toml" << 'EOF'
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = 7860

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#1f2937"
EOF
    
    # Copy application files
    echo -e "${YELLOW}📁 Copying application files...${NC}"
    
    # Copy main application files
    if [ -f "${PROJECT_ROOT}/streamlit_app.py" ]; then
        cp "${PROJECT_ROOT}/streamlit_app.py" "$temp_dir/"
    fi
    
    if [ -f "${PROJECT_ROOT}/mcp_agent.py" ]; then
        cp "${PROJECT_ROOT}/mcp_agent.py" "$temp_dir/"
    fi
    
    if [ -f "${PROJECT_ROOT}/knowledge_service.py" ]; then
        cp "${PROJECT_ROOT}/knowledge_service.py" "$temp_dir/"
    fi
    
    # Copy knowledge base files (if they exist and are not too large)
    if [ -d "${PROJECT_ROOT}/knowledge_base_pdfs" ]; then
        echo -e "${YELLOW}📚 Copying knowledge base files...${NC}"
        cp -r "${PROJECT_ROOT}/knowledge_base_pdfs" "$temp_dir/" || echo "⚠️ Some knowledge base files may be too large"
    fi
    
    echo "$temp_dir"
}

deploy_to_huggingface() {
    echo -e "${YELLOW}🚀 Deploying to HuggingFace Spaces...${NC}"
    
    local temp_dir=$(create_huggingface_files)
    
    # Initialize git repository
    cd "$temp_dir"
    git init
    git lfs track "*.pdf" "*.pkl" "*.bin" "*.model"
    
    # Set git config
    git config user.name "$(huggingface-cli whoami)"
    git config user.email "noreply@huggingface.co"
    
    # Add HuggingFace remote
    git remote add origin "https://huggingface.co/spaces/${USERNAME}/${SPACE_NAME}"
    
    # Add all files
    git add .
    git commit -m "Initial deployment of AI Customer Service Platform to HuggingFace Spaces

- Streamlit-based customer service interface
- AI-powered chat with RAG capabilities
- Knowledge base integration
- Real-time analytics dashboard
- Production-ready deployment

🤖 Built for AI Enterprise Accelerator Training"
    
    # Push to HuggingFace
    echo -e "${YELLOW}📤 Pushing to HuggingFace Spaces...${NC}"
    
    # Try to push, create space if it doesn't exist
    if ! git push origin main 2>/dev/null; then
        echo -e "${YELLOW}📝 Creating new space...${NC}"
        
        # Create space using huggingface-cli
        huggingface-cli repo create \
            "${USERNAME}/${SPACE_NAME}" \
            --type=space \
            --space_sdk="${SDK}" \
            --private=$([ "$VISIBILITY" = "private" ] && echo "true" || echo "false") \
            2>/dev/null || echo "Space may already exist"
        
        # Try push again
        sleep 2
        if git push origin main; then
            echo -e "${GREEN}✅ Successfully deployed to HuggingFace Spaces${NC}"
        else
            echo -e "${RED}❌ Failed to push to HuggingFace Spaces${NC}"
            echo "Please check your credentials and space permissions"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Successfully deployed to HuggingFace Spaces${NC}"
    fi
    
    # Cleanup
    cd - > /dev/null
    rm -rf "$temp_dir"
    
    local space_url="https://huggingface.co/spaces/${USERNAME}/${SPACE_NAME}"
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo "=================================================="
    echo -e "${GREEN}🌐 Space URL: ${space_url}${NC}"
    echo -e "${GREEN}⚙️ Settings: ${space_url}/settings${NC}"
    echo -e "${GREEN}📊 Analytics: ${space_url}/analytics${NC}"
    echo ""
    echo "📝 Next steps:"
    echo "1. Visit your space URL to see the deployed application"
    echo "2. Wait a few minutes for the initial build to complete"
    echo "3. Check the build logs if there are any issues"
    echo "4. Share your space with the community!"
    echo "5. Monitor usage and feedback in the Community tab"
    echo ""
    
    # Optional: Open in browser
    read -p "Would you like to open the space in your browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v open &> /dev/null; then
            open "$space_url"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "$space_url"
        else
            echo "Please visit: $space_url"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --username)
            USERNAME="$2"
            shift 2
            ;;
        --space-name)
            SPACE_NAME="$2"
            shift 2
            ;;
        --sdk)
            SDK="$2"
            shift 2
            ;;
        --visibility)
            VISIBILITY="$2"
            shift 2
            ;;
        --license)
            LICENSE="$2"
            shift 2
            ;;
        --interactive)
            INTERACTIVE=true
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Main script execution
print_banner
check_prerequisites

if [ "$INTERACTIVE" = true ] || [ -z "$USERNAME" ]; then
    interactive_setup
fi

# Set defaults if not provided
SPACE_NAME=${SPACE_NAME:-ai-customer-service}

# Validate required parameters
if [ -z "$USERNAME" ]; then
    echo -e "${RED}❌ Username is required${NC}"
    print_usage
    exit 1
fi

# Deploy to HuggingFace Spaces
deploy_to_huggingface

echo -e "${GREEN}✅ HuggingFace Spaces deployment completed${NC}"