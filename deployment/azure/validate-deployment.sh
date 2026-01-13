#!/bin/bash

# Pre-deployment validation script
# This script checks if your app is ready for Azure deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo "========================================="
echo "Azure Deployment Validation"
echo "========================================="
echo ""

# Function to check if a file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check if a directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 directory is missing"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Check required files
echo "Checking required files..."
check_file "runtime.txt"
check_file "requirements.txt"
check_file "startup.sh"
check_file ".deployment"
check_file ".azure-include"
check_file "app/main.py"
echo ""

# Check required directories
echo "Checking required directories..."
check_dir "app"
check_dir "data/documents"
echo ""

# Check if startup.sh is executable
echo "Checking file permissions..."
if [ -x "startup.sh" ]; then
    echo -e "${GREEN}✓${NC} startup.sh is executable"
else
    echo -e "${YELLOW}⚠${NC} startup.sh is not executable (will be fixed automatically)"
    chmod +x startup.sh
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check Python version in runtime.txt
echo "Checking Python version..."
if grep -q "python-3.11" runtime.txt; then
    echo -e "${GREEN}✓${NC} Python 3.11 specified in runtime.txt"
else
    echo -e "${RED}✗${NC} runtime.txt should specify Python 3.11"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check if critical dependencies are in requirements.txt
echo "Checking critical dependencies..."
REQUIRED_DEPS=("fastapi" "uvicorn" "openai" "langchain" "faiss-cpu" "gunicorn")
for dep in "${REQUIRED_DEPS[@]}"; do
    if grep -q "$dep" requirements.txt; then
        echo -e "${GREEN}✓${NC} $dep found in requirements.txt"
    else
        echo -e "${RED}✗${NC} $dep missing in requirements.txt"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check if documents exist
echo "Checking for documents..."
DOC_COUNT=$(find data/documents -type f -name "*.txt" -o -name "*.md" -o -name "*.pdf" 2>/dev/null | wc -l)
if [ $DOC_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $DOC_COUNT document(s) in data/documents/"
else
    echo -e "${YELLOW}⚠${NC} No documents found in data/documents/ (app will work but without document retrieval)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check Azure CLI
echo "Checking Azure CLI..."
if command -v az &> /dev/null; then
    echo -e "${GREEN}✓${NC} Azure CLI is installed"
    
    # Check if logged in
    if az account show &> /dev/null; then
        SUBSCRIPTION=$(az account show --query name -o tsv)
        echo -e "${GREEN}✓${NC} Logged in to Azure (Subscription: $SUBSCRIPTION)"
    else
        echo -e "${YELLOW}⚠${NC} Not logged in to Azure (run 'az login')"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗${NC} Azure CLI is not installed"
    echo "   Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check Git status
echo "Checking Git status..."
if git status &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git repository initialized"
    
    # Check for uncommitted changes
    if [ -z "$(git status --porcelain)" ]; then
        echo -e "${GREEN}✓${NC} No uncommitted changes"
    else
        echo -e "${YELLOW}⚠${NC} You have uncommitted changes"
        echo "   Run 'git add . && git commit -m \"Prepare for deployment\"' before deploying"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗${NC} Not a Git repository"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check .env file (should not be committed)
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists (for local development)"
    
    # Check if .env is in .gitignore
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo -e "${GREEN}✓${NC} .env is in .gitignore (good!)"
    else
        echo -e "${YELLOW}⚠${NC} .env should be in .gitignore"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check for OpenAI API key
    if grep -q "OPENAI_API_KEY=" .env; then
        if grep -q "OPENAI_API_KEY=sk-" .env; then
            echo -e "${GREEN}✓${NC} OpenAI API key configured in .env"
        else
            echo -e "${YELLOW}⚠${NC} OpenAI API key in .env might not be set correctly"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} .env file not found (okay for deployment, needed for local testing)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo "Next step: Run the deployment script"
    echo "  ./deployment/azure/deploy-improved.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    echo ""
    echo "You can proceed with deployment, but review warnings above."
    echo ""
    echo "Next step: Run the deployment script"
    echo "  ./deployment/azure/deploy-improved.sh"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) and $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    exit 1
fi
