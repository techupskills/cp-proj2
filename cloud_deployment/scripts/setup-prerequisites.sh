#!/bin/bash

# Prerequisites Setup Script for AI Customer Service Platform Cloud Deployment
# This script helps install and configure the necessary tools for cloud deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    Prerequisites Setup Script                               ║"
    echo "║                 AI Customer Service Platform                                 ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all           Install all prerequisites (Docker, AWS CLI, gcloud, Azure CLI)"
    echo "  --docker        Install Docker"
    echo "  --aws           Install AWS CLI"
    echo "  --gcp           Install Google Cloud CLI"
    echo "  --azure         Install Azure CLI"
    echo "  --check         Check current installation status"
    echo "  --help, -h      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all          Install all cloud CLI tools"
    echo "  $0 --aws --gcp    Install AWS and GCP CLI tools"
    echo "  $0 --check        Check what's already installed"
    echo ""
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    echo -e "${BLUE}Detected OS: ${OS}${NC}"
}

check_prerequisites() {
    echo -e "${YELLOW}🔍 Checking current installation status...${NC}"
    echo ""
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        echo -e "  ${GREEN}✅ Docker installed (${DOCKER_VERSION})${NC}"
        
        if docker info &> /dev/null; then
            echo -e "  ${GREEN}✅ Docker daemon running${NC}"
        else
            echo -e "  ${YELLOW}⚠️ Docker installed but daemon not running${NC}"
        fi
    else
        echo -e "  ${RED}❌ Docker not installed${NC}"
    fi
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version | cut -d' ' -f1 | cut -d'/' -f2)
        echo -e "  ${GREEN}✅ AWS CLI installed (${AWS_VERSION})${NC}"
        
        if aws sts get-caller-identity &> /dev/null; then
            echo -e "  ${GREEN}✅ AWS credentials configured${NC}"
        else
            echo -e "  ${YELLOW}⚠️ AWS CLI installed but not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ AWS CLI not installed${NC}"
    fi
    
    # Check Google Cloud CLI
    if command -v gcloud &> /dev/null; then
        GCLOUD_VERSION=$(gcloud version --format="value(Google Cloud SDK)")
        echo -e "  ${GREEN}✅ Google Cloud CLI installed (${GCLOUD_VERSION})${NC}"
        
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 | grep -q "."; then
            echo -e "  ${GREEN}✅ GCP credentials configured${NC}"
        else
            echo -e "  ${YELLOW}⚠️ Google Cloud CLI installed but not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ Google Cloud CLI not installed${NC}"
    fi
    
    # Check Azure CLI
    if command -v az &> /dev/null; then
        AZURE_VERSION=$(az version --query '"azure-cli"' -o tsv)
        echo -e "  ${GREEN}✅ Azure CLI installed (${AZURE_VERSION})${NC}"
        
        if az account show &> /dev/null; then
            echo -e "  ${GREEN}✅ Azure credentials configured${NC}"
        else
            echo -e "  ${YELLOW}⚠️ Azure CLI installed but not configured${NC}"
        fi
    else
        echo -e "  ${RED}❌ Azure CLI not installed${NC}"
    fi
    
    echo ""
}

install_docker() {
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    
    case $OS in
        "debian")
            echo "Installing Docker on Debian/Ubuntu..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            echo -e "${GREEN}✅ Docker installed. Please log out and back in to use Docker without sudo.${NC}"
            ;;
        "redhat")
            echo "Installing Docker on Red Hat/CentOS..."
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            echo -e "${GREEN}✅ Docker installed and started${NC}"
            ;;
        "macos")
            echo "Please install Docker Desktop for Mac from: https://docs.docker.com/desktop/install/mac-install/"
            echo "Or use Homebrew: brew install --cask docker"
            ;;
        "windows")
            echo "Please install Docker Desktop for Windows from: https://docs.docker.com/desktop/install/windows-install/"
            ;;
        *)
            echo -e "${RED}❌ Unsupported OS for automatic Docker installation${NC}"
            ;;
    esac
}

install_aws_cli() {
    echo -e "${YELLOW}☁️ Installing AWS CLI...${NC}"
    
    case $OS in
        "linux"|"debian"|"redhat")
            echo "Installing AWS CLI on Linux..."
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            unzip -q awscliv2.zip
            sudo ./aws/install
            rm -rf awscliv2.zip aws/
            echo -e "${GREEN}✅ AWS CLI installed${NC}"
            ;;
        "macos")
            echo "Installing AWS CLI on macOS..."
            curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
            sudo installer -pkg AWSCLIV2.pkg -target /
            rm AWSCLIV2.pkg
            echo -e "${GREEN}✅ AWS CLI installed${NC}"
            ;;
        "windows")
            echo "Please download and install AWS CLI from: https://aws.amazon.com/cli/"
            ;;
        *)
            echo -e "${RED}❌ Unsupported OS for automatic AWS CLI installation${NC}"
            ;;
    esac
    
    echo ""
    echo "To configure AWS CLI, run: aws configure"
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region name (e.g., us-east-1)"
    echo "  - Default output format (json)"
}

install_gcloud() {
    echo -e "${YELLOW}☁️ Installing Google Cloud CLI...${NC}"
    
    case $OS in
        "linux"|"debian"|"redhat")
            echo "Installing Google Cloud CLI on Linux..."
            curl https://sdk.cloud.google.com | bash
            echo -e "${GREEN}✅ Google Cloud CLI installed${NC}"
            echo -e "${YELLOW}Please restart your shell or run: source ~/.bashrc${NC}"
            ;;
        "macos")
            echo "Installing Google Cloud CLI on macOS..."
            curl https://sdk.cloud.google.com | bash
            echo -e "${GREEN}✅ Google Cloud CLI installed${NC}"
            echo -e "${YELLOW}Please restart your shell or run: source ~/.bash_profile${NC}"
            ;;
        "windows")
            echo "Please download and install Google Cloud CLI from: https://cloud.google.com/sdk/docs/install"
            ;;
        *)
            echo -e "${RED}❌ Unsupported OS for automatic Google Cloud CLI installation${NC}"
            ;;
    esac
    
    echo ""
    echo "To configure Google Cloud CLI, run:"
    echo "  gcloud init"
    echo "  gcloud auth login"
    echo "  gcloud config set project YOUR_PROJECT_ID"
}

install_azure_cli() {
    echo -e "${YELLOW}☁️ Installing Azure CLI...${NC}"
    
    case $OS in
        "debian")
            echo "Installing Azure CLI on Debian/Ubuntu..."
            curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
            echo -e "${GREEN}✅ Azure CLI installed${NC}"
            ;;
        "redhat")
            echo "Installing Azure CLI on Red Hat/CentOS..."
            sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
            echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo
            sudo yum install azure-cli
            echo -e "${GREEN}✅ Azure CLI installed${NC}"
            ;;
        "macos")
            echo "Installing Azure CLI on macOS..."
            if command -v brew &> /dev/null; then
                brew update && brew install azure-cli
                echo -e "${GREEN}✅ Azure CLI installed via Homebrew${NC}"
            else
                echo "Homebrew not found. Please install Homebrew first or download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
            fi
            ;;
        "windows")
            echo "Please download and install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows"
            ;;
        *)
            echo -e "${RED}❌ Unsupported OS for automatic Azure CLI installation${NC}"
            ;;
    esac
    
    echo ""
    echo "To configure Azure CLI, run: az login"
}

install_additional_tools() {
    echo -e "${YELLOW}🔧 Installing additional useful tools...${NC}"
    
    case $OS in
        "debian")
            sudo apt-get update
            sudo apt-get install -y curl wget git unzip jq
            ;;
        "redhat")
            sudo yum install -y curl wget git unzip jq
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install curl wget git jq
            else
                echo "Homebrew not found. Please install Homebrew for easier tool management."
            fi
            ;;
    esac
    
    echo -e "${GREEN}✅ Additional tools installed${NC}"
}

main() {
    print_banner
    detect_os
    
    if [ $# -eq 0 ]; then
        echo "No options specified. Use --help for usage information."
        echo "To check current status: $0 --check"
        echo "To install everything: $0 --all"
        exit 0
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                install_additional_tools
                install_docker
                install_aws_cli
                install_gcloud
                install_azure_cli
                shift
                ;;
            --docker)
                install_docker
                shift
                ;;
            --aws)
                install_aws_cli
                shift
                ;;
            --gcp)
                install_gcloud
                shift
                ;;
            --azure)
                install_azure_cli
                shift
                ;;
            --check)
                check_prerequisites
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
    
    echo ""
    echo -e "${GREEN}🎉 Prerequisites setup completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure your cloud CLI tools with credentials"
    echo "2. Verify installations with: $0 --check"
    echo "3. Run the cloud deployment script: ../scripts/cloud-deploy.sh --check"
    echo ""
}

# Run main function with all arguments
main "$@"