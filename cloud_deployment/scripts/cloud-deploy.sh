#!/bin/bash

# Universal Cloud Deployment Script for AI Customer Service Platform
# This script provides a unified interface to deploy to AWS, GCP, or Azure

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

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    AI Customer Service Platform                              ║"
    echo "║                       Universal Cloud Deployer                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo "Usage: $0 [CLOUD_PROVIDER] [OPTIONS]"
    echo ""
    echo "Cloud Providers:"
    echo "  aws           Deploy to Amazon Web Services (App Runner)"
    echo "  gcp           Deploy to Google Cloud Platform (Cloud Run)"
    echo "  azure         Deploy to Microsoft Azure (Container Instances)"
    echo "  huggingface   Deploy to HuggingFace Spaces (Streamlit)"
    echo "  interactive   Interactive mode - choose provider and options"
    echo ""
    echo "Options:"
    echo "  --help, -h      Show this help message"
    echo "  --check         Check prerequisites for all cloud providers"
    echo "  --config        Show current configuration"
    echo ""
    echo "Examples:"
    echo "  $0 aws                    Deploy to AWS App Runner"
    echo "  $0 gcp                    Deploy to Google Cloud Run"  
    echo "  $0 azure                  Deploy to Azure Container Instances"
    echo "  $0 huggingface            Deploy to HuggingFace Spaces"
    echo "  $0 interactive            Interactive deployment wizard"
    echo "  $0 --check                Check all prerequisites"
    echo ""
}

check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites for all cloud providers...${NC}"
    echo ""
    
    # General prerequisites
    echo -e "${BLUE}General Prerequisites:${NC}"
    
    if command -v docker &> /dev/null; then
        echo -e "  ${GREEN}✅ Docker installed${NC}"
    else
        echo -e "  ${RED}❌ Docker not installed${NC}"
    fi
    
    if command -v git &> /dev/null; then
        echo -e "  ${GREEN}✅ Git installed${NC}"
    else
        echo -e "  ${RED}❌ Git not installed${NC}"
    fi
    
    if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
        echo -e "  ${GREEN}✅ Requirements.txt found${NC}"
    else
        echo -e "  ${RED}❌ Requirements.txt not found${NC}"
    fi
    
    if [ -f "${PROJECT_ROOT}/Dockerfile" ]; then
        echo -e "  ${GREEN}✅ Dockerfile found${NC}"
    else
        echo -e "  ${RED}❌ Dockerfile not found${NC}"
    fi
    
    echo ""
    
    # AWS Prerequisites
    echo -e "${BLUE}AWS Prerequisites:${NC}"
    
    if command -v aws &> /dev/null; then
        echo -e "  ${GREEN}✅ AWS CLI installed${NC}"
        if aws sts get-caller-identity &> /dev/null; then
            echo -e "  ${GREEN}✅ AWS credentials configured${NC}"
            ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
            REGION=$(aws configure get region || echo "not set")
            echo -e "  ${GREEN}   Account: ${ACCOUNT_ID}${NC}"
            echo -e "  ${GREEN}   Region: ${REGION}${NC}"
        else
            echo -e "  ${RED}❌ AWS credentials not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ AWS CLI not installed${NC}"
    fi
    
    echo ""
    
    # GCP Prerequisites  
    echo -e "${BLUE}GCP Prerequisites:${NC}"
    
    if command -v gcloud &> /dev/null; then
        echo -e "  ${GREEN}✅ Google Cloud CLI installed${NC}"
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 | grep -q "."; then
            echo -e "  ${GREEN}✅ GCP credentials configured${NC}"
            PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "not set")
            REGION=$(gcloud config get-value compute/region 2>/dev/null || echo "not set")
            echo -e "  ${GREEN}   Project: ${PROJECT_ID}${NC}"
            echo -e "  ${GREEN}   Region: ${REGION}${NC}"
        else
            echo -e "  ${RED}❌ GCP credentials not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ Google Cloud CLI not installed${NC}"
    fi
    
    echo ""
    
    # Azure Prerequisites
    echo -e "${BLUE}Azure Prerequisites:${NC}"
    
    if command -v az &> /dev/null; then
        echo -e "  ${GREEN}✅ Azure CLI installed${NC}"
        if az account show &> /dev/null; then
            echo -e "  ${GREEN}✅ Azure credentials configured${NC}"
            SUBSCRIPTION=$(az account show --query name --output tsv)
            TENANT=$(az account show --query tenantId --output tsv)
            echo -e "  ${GREEN}   Subscription: ${SUBSCRIPTION}${NC}"
            echo -e "  ${GREEN}   Tenant: ${TENANT}${NC}"
        else
            echo -e "  ${RED}❌ Azure credentials not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ Azure CLI not installed${NC}"
    fi
    
    echo ""
    
    # HuggingFace Prerequisites
    echo -e "${BLUE}HuggingFace Prerequisites:${NC}"
    
    if command -v huggingface-cli &> /dev/null; then
        echo -e "  ${GREEN}✅ HuggingFace CLI installed${NC}"
        if huggingface-cli whoami &> /dev/null; then
            echo -e "  ${GREEN}✅ HuggingFace credentials configured${NC}"
            USERNAME=$(huggingface-cli whoami 2>/dev/null | head -n 1 || echo "unknown")
            echo -e "  ${GREEN}   Username: ${USERNAME}${NC}"
        else
            echo -e "  ${RED}❌ HuggingFace credentials not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ HuggingFace CLI not installed${NC}"
    fi
    
    echo ""
}

show_config() {
    echo -e "${YELLOW}⚙️ Current Configuration:${NC}"
    echo ""
    echo "Project Root: ${PROJECT_ROOT}"
    echo "Script Directory: ${SCRIPT_DIR}"
    echo ""
    
    if [ -f "${PROJECT_ROOT}/.env" ]; then
        echo "Environment file found: ${PROJECT_ROOT}/.env"
        echo "Contents:"
        cat "${PROJECT_ROOT}/.env" | grep -v "^#" | head -10
    else
        echo "No .env file found"
    fi
    
    echo ""
}

interactive_deploy() {
    echo -e "${BLUE}🎯 Interactive Deployment Wizard${NC}"
    echo "=================================================="
    
    # Choose cloud provider
    echo ""
    echo "Select cloud provider:"
    echo "1) Amazon Web Services (AWS)"
    echo "2) Google Cloud Platform (GCP)" 
    echo "3) Microsoft Azure"
    echo "4) HuggingFace Spaces"
    echo ""
    
    while true; do
        read -p "Enter choice (1-4): " choice
        case $choice in
            1)
                CLOUD_PROVIDER="aws"
                break
                ;;
            2)
                CLOUD_PROVIDER="gcp"
                break
                ;;
            3)
                CLOUD_PROVIDER="azure"
                break
                ;;
            4)
                CLOUD_PROVIDER="huggingface"
                break
                ;;
            *)
                echo "Invalid choice. Please enter 1-4."
                ;;
        esac
    done
    
    echo -e "${GREEN}Selected: ${CLOUD_PROVIDER}${NC}"
    echo ""
    
    # Choose deployment options
    case $CLOUD_PROVIDER in
        "aws")
            echo "AWS Deployment Options:"
            echo "1) App Runner (Recommended - Serverless)"
            echo "2) ECS with Fargate (Container orchestration)"
            echo "3) Lambda (Serverless functions)"
            echo ""
            
            while true; do
                read -p "Enter choice (1-3): " aws_choice
                case $aws_choice in
                    1)
                        AWS_SERVICE="apprunner"
                        break
                        ;;
                    2)
                        AWS_SERVICE="ecs"
                        break
                        ;;
                    3)
                        AWS_SERVICE="lambda"
                        break
                        ;;
                    *)
                        echo "Invalid choice. Please enter 1, 2, or 3."
                        ;;
                esac
            done
            ;;
        "gcp")
            echo "GCP Deployment Options:"
            echo "1) Cloud Run (Recommended - Serverless containers)"
            echo "2) Google Kubernetes Engine (GKE)"
            echo "3) Compute Engine (Virtual machines)"
            echo ""
            
            while true; do
                read -p "Enter choice (1-3): " gcp_choice
                case $gcp_choice in
                    1)
                        GCP_SERVICE="cloudrun"
                        break
                        ;;
                    2)
                        GCP_SERVICE="gke"
                        break
                        ;;
                    3)
                        GCP_SERVICE="computeengine"
                        break
                        ;;
                    *)
                        echo "Invalid choice. Please enter 1, 2, or 3."
                        ;;
                esac
            done
            ;;
        "azure")
            echo "Azure Deployment Options:"
            echo "1) Container Instances (Recommended - Simple containers)"
            echo "2) Container Apps (Serverless containers)"
            echo "3) Azure Kubernetes Service (AKS)"
            echo ""
            
            while true; do
                read -p "Enter choice (1-3): " azure_choice
                case $azure_choice in
                    1)
                        AZURE_SERVICE="aci"
                        break
                        ;;
                    2)
                        AZURE_SERVICE="containerapp"
                        break
                        ;;
                    3)
                        AZURE_SERVICE="aks"
                        break
                        ;;
                    *)
                        echo "Invalid choice. Please enter 1, 2, or 3."
                        ;;
                esac
            done
            ;;
        "huggingface")
            echo "HuggingFace Spaces Deployment Options:"
            echo "1) Streamlit Space (Recommended - Easy sharing)"
            echo "2) Gradio Space (ML-focused interface)"
            echo "3) Docker Space (Custom container)"
            echo ""
            
            while true; do
                read -p "Enter choice (1-3): " hf_choice
                case $hf_choice in
                    1)
                        HF_SDK="streamlit"
                        break
                        ;;
                    2)
                        HF_SDK="gradio"
                        break
                        ;;
                    3)
                        HF_SDK="docker"
                        break
                        ;;
                    *)
                        echo "Invalid choice. Please enter 1, 2, or 3."
                        ;;
                esac
            done
            ;;
    esac
    
    # Confirm deployment
    echo ""
    echo -e "${YELLOW}📋 Deployment Summary:${NC}"
    echo "  Cloud Provider: ${CLOUD_PROVIDER}"
    case $CLOUD_PROVIDER in
        "aws") echo "  Service: ${AWS_SERVICE}" ;;
        "gcp") echo "  Service: ${GCP_SERVICE}" ;;
        "azure") echo "  Service: ${AZURE_SERVICE}" ;;
        "huggingface") echo "  SDK: ${HF_SDK}" ;;
    esac
    echo ""
    
    read -p "Proceed with deployment? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_to_cloud $CLOUD_PROVIDER
    else
        echo "Deployment cancelled."
        exit 0
    fi
}

deploy_to_cloud() {
    local cloud_provider=$1
    
    echo -e "${GREEN}🚀 Starting deployment to ${cloud_provider}...${NC}"
    
    # Change to project root directory
    cd "${PROJECT_ROOT}"
    
    case $cloud_provider in
        "aws")
            if [ -f "${PROJECT_ROOT}/cloud_deployment/aws/deploy-to-aws-apprunner.sh" ]; then
                echo -e "${YELLOW}📦 Running AWS App Runner deployment...${NC}"
                bash "${PROJECT_ROOT}/cloud_deployment/aws/deploy-to-aws-apprunner.sh"
            else
                echo -e "${RED}❌ AWS deployment script not found${NC}"
                exit 1
            fi
            ;;
        "gcp")
            if [ -f "${PROJECT_ROOT}/cloud_deployment/gcp/deploy-to-cloud-run.sh" ]; then
                echo -e "${YELLOW}📦 Running GCP Cloud Run deployment...${NC}"
                bash "${PROJECT_ROOT}/cloud_deployment/gcp/deploy-to-cloud-run.sh"
            else
                echo -e "${RED}❌ GCP deployment script not found${NC}"
                exit 1
            fi
            ;;
        "azure")
            if [ -f "${PROJECT_ROOT}/cloud_deployment/azure/deploy-to-azure-aci.sh" ]; then
                echo -e "${YELLOW}📦 Running Azure Container Instances deployment...${NC}"
                bash "${PROJECT_ROOT}/cloud_deployment/azure/deploy-to-azure-aci.sh"
            else
                echo -e "${RED}❌ Azure deployment script not found${NC}"
                exit 1
            fi
            ;;
        "huggingface")
            if [ -f "${PROJECT_ROOT}/cloud_deployment/huggingface/deploy-to-huggingface.sh" ]; then
                echo -e "${YELLOW}📦 Running HuggingFace Spaces deployment...${NC}"
                bash "${PROJECT_ROOT}/cloud_deployment/huggingface/deploy-to-huggingface.sh" --interactive
            else
                echo -e "${RED}❌ HuggingFace deployment script not found${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Unsupported cloud provider: $cloud_provider${NC}"
            exit 1
            ;;
    esac
}

# Main script logic
print_banner

case "${1:-}" in
    "aws"|"gcp"|"azure")
        deploy_to_cloud "$1"
        ;;
    "interactive"|"")
        interactive_deploy
        ;;
    "--check")
        check_prerequisites
        ;;
    "--config")
        show_config
        ;;
    "--help"|"-h")
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac