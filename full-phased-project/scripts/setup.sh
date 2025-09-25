#!/bin/bash

# Full Phased Data Engineering Project Setup Script
# =================================================

set -e  # Exit on any error

echo "🚀 Setting up Full Phased Data Engineering Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Check if running from project root
if [ ! -f "README.md" ] || [ ! -d "phase1-batch-etl" ]; then
    print_error "Please run this script from the full-phased-project root directory"
    exit 1
fi

print_header "Environment Setup"

# Create necessary directories
print_status "Creating directory structure..."
mkdir -p {data/{raw,processed,output},logs,tmp}
mkdir -p {docs/{architecture,api,deployment},tests,config}

# Create .gitkeep files for empty directories
touch data/raw/.gitkeep data/processed/.gitkeep data/output/.gitkeep logs/.gitkeep

print_header "Python Environment Setup"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "Detected Python version: $python_version"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    print_error "Python 3.8+ is required. Please install a compatible version."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install main requirements
print_status "Installing main requirements..."
pip install -r requirements.txt

# Install phase-specific requirements
print_status "Installing Phase 1 requirements..."
pip install -r phase1-batch-etl/requirements.txt

print_status "Installing Phase 2 requirements..."
pip install -r phase2-streaming-orchestration/requirements.txt

print_status "Installing Phase 3 requirements..."
pip install -r phase3-cloud-pipeline/requirements.txt

print_header "Configuration Setup"

# Copy environment template
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration"
fi

# Copy phase configurations
if [ ! -f "phase1-batch-etl/config/config.ini" ]; then
    print_warning "Phase 1 config.ini already exists. Please verify your database settings."
fi

print_header "Docker Setup Check"

# Check if Docker is installed
if command -v docker &> /dev/null; then
    print_status "Docker is installed: $(docker --version)"
    
    # Check if Docker Compose is available
    if command -v docker-compose &> /dev/null; then
        print_status "Docker Compose is installed: $(docker-compose --version)"
    elif docker compose version &> /dev/null; then
        print_status "Docker Compose (v2) is installed: $(docker compose version)"
    else
        print_warning "Docker Compose not found. Some features may not work."
    fi
else
    print_warning "Docker not found. Please install Docker for full functionality."
fi

print_header "AWS CLI Setup Check"

# Check if AWS CLI is installed
if command -v aws &> /dev/null; then
    print_status "AWS CLI is installed: $(aws --version)"
    
    # Check if AWS credentials are configured
    if aws sts get-caller-identity &> /dev/null; then
        print_status "AWS credentials are configured"
    else
        print_warning "AWS credentials not configured. Run 'aws configure' for Phase 3."
    fi
else
    print_warning "AWS CLI not found. Please install for Phase 3 (Cloud Pipeline)."
fi

print_header "Terraform Setup Check"

# Check if Terraform is installed
if command -v terraform &> /dev/null; then
    print_status "Terraform is installed: $(terraform --version | head -n1)"
else
    print_warning "Terraform not found. Please install for Phase 3 infrastructure deployment."
fi

print_header "Database Setup"

# Check if PostgreSQL is available
if command -v psql &> /dev/null; then
    print_status "PostgreSQL client is installed"
    print_status "Please ensure PostgreSQL server is running for Phase 1"
else
    print_warning "PostgreSQL client not found. Install PostgreSQL or use Docker."
fi

print_header "Final Setup Steps"

# Create sample data directories
mkdir -p data/raw/covid-samples data/processed/covid-samples

# Set up pre-commit hooks if available
if command -v pre-commit &> /dev/null; then
    print_status "Setting up pre-commit hooks..."
    pre-commit install
fi

print_header "Setup Complete! 🎉"

echo ""
print_status "Next steps:"
echo "  1. Edit .env file with your configuration"
echo "  2. Start Docker services: make docker-up"
echo "  3. Run Phase 1: make run-phase1"
echo "  4. Run Phase 2: make run-phase2"
echo "  5. Deploy Phase 3: make deploy-infrastructure"
echo ""
print_status "Quick start commands:"
echo "  - make help              # Show all available commands"
echo "  - make dev-setup         # Complete development setup"
echo "  - make test              # Run all tests"
echo "  - make run-all           # Run all phases"
echo ""
print_status "Documentation:"
echo "  - README.md              # Main project documentation"
echo "  - phase*/README.md       # Phase-specific documentation"
echo "  - docs/                  # Additional documentation"
echo ""

# Show summary
echo -e "\n${GREEN}✅ Setup completed successfully!${NC}"
echo "Virtual environment: $(pwd)/venv"
echo "Python version: $python_version"
echo "Project root: $(pwd)"

print_warning "Remember to activate the virtual environment: source venv/bin/activate"