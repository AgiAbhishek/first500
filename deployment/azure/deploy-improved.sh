#!/bin/bash

# Azure App Service Deployment Script for AI RAG Agent (IMPROVED)
# This script deploys the application to Azure App Service with enhanced error handling

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="ai-rag-agent-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="ai-rag-agent-plan"
WEB_APP_NAME="ai-rag-agent-$(date +%s)"  # Unique name with timestamp
RUNTIME="PYTHON:3.11"
SKU="B1"  # Basic tier - change to F1 for free tier

echo "========================================="
echo "AI RAG Agent - Azure Deployment"
echo "========================================="
echo ""

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Azure CLI is installed
echo "Checking prerequisites..."
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi
print_success "Azure CLI is installed"

# Check if logged in
echo "Checking Azure login status..."
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Initiating login..."
    az login
else
    print_success "Already logged in to Azure"
fi

# Get subscription info
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_success "Using subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
echo ""

# Confirm before proceeding
echo "========================================="
echo "Deployment Configuration:"
echo "========================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "App Service Plan: $APP_SERVICE_PLAN"
echo "Web App Name: $WEB_APP_NAME"
echo "Runtime: $RUNTIME"
echo "SKU: $SKU"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    print_warning "Deployment cancelled."
    exit 0
fi
echo ""

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP..."
if az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table > /dev/null 2>&1; then
    print_success "Resource group created: $RESOURCE_GROUP"
else
    print_warning "Resource group already exists or creation failed (continuing...)"
fi

# Create App Service Plan
echo "Creating App Service Plan: $APP_SERVICE_PLAN..."
if az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux \
    --output table > /dev/null 2>&1; then
    print_success "App Service Plan created: $APP_SERVICE_PLAN"
else
    print_warning "App Service Plan already exists or creation failed (continuing...)"
fi

# Create Web App
echo "Creating Web App: $WEB_APP_NAME..."
if az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --runtime $RUNTIME \
    --output table > /dev/null 2>&1; then
    print_success "Web App created: $WEB_APP_NAME"
else
    print_error "Failed to create Web App"
    exit 1
fi

# Configure startup command
echo "Configuring startup command..."
if az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --startup-file "startup.sh" \
    --output none; then
    print_success "Startup command configured"
else
    print_error "Failed to configure startup command"
    exit 1
fi

# Enable logging
echo "Enabling application logging..."
if az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --application-logging filesystem \
    --level information \
    --output none; then
    print_success "Application logging enabled"
else
    print_warning "Failed to enable logging (continuing...)"
fi

# Configure deployment source (Local Git)
echo "Setting up local Git deployment..."
if az webapp deployment source config-local-git \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --output none; then
    print_success "Local Git deployment configured"
else
    print_error "Failed to configure Git deployment"
    exit 1
fi

# Get deployment credentials
echo "Retrieving deployment credentials..."
DEPLOYMENT_USER=$(az webapp deployment list-publishing-credentials \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query publishingUserName -o tsv)

# Get deployment URL
GIT_URL=$(az webapp deployment source show \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query repositoryUrl -o tsv 2>/dev/null || echo "")

if [ -z "$GIT_URL" ]; then
    # Construct Git URL manually if not available
    GIT_URL="https://$WEB_APP_NAME.scm.azurewebsites.net/$WEB_APP_NAME.git"
fi

# Get app URL
APP_URL=$(az webapp show \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query defaultHostName -o tsv)

# Save deployment info to file
DEPLOYMENT_INFO_FILE="deployment/azure/deployment-info.txt"
cat > $DEPLOYMENT_INFO_FILE << EOF
========================================
Azure Deployment Information
========================================
Deployed at: $(date)
Resource Group: $RESOURCE_GROUP
App Service Plan: $APP_SERVICE_PLAN
Web App Name: $WEB_APP_NAME
App URL: https://$APP_URL
Git URL: $GIT_URL
Deployment User: $DEPLOYMENT_USER
========================================
EOF

print_success "Deployment information saved to $DEPLOYMENT_INFO_FILE"

echo ""
echo "========================================="
echo -e "${GREEN}✓ Deployment Configuration Complete!${NC}"
echo "========================================="
echo ""
echo "Web App Name: $WEB_APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "App URL: https://$APP_URL"
echo "Git URL: $GIT_URL"
echo ""
echo "========================================="
echo "NEXT STEPS:"
echo "========================================="
echo ""
echo "1. Set environment variables:"
echo ""
echo "   az webapp config appsettings set \\"
echo "       --resource-group $RESOURCE_GROUP \\"
echo "       --name $WEB_APP_NAME \\"
echo "       --settings \\"
echo "           OPENAI_API_KEY='YOUR_OPENAI_API_KEY_HERE' \\"
echo "           OPENAI_MODEL='gpt-4-turbo-preview' \\"
echo "           OPENAI_EMBEDDING_MODEL='text-embedding-3-small' \\"
echo "           ENVIRONMENT='production' \\"
echo "           LOG_LEVEL='INFO' \\"
echo "           CORS_ORIGINS='*'"
echo ""
print_warning "IMPORTANT: Replace 'YOUR_OPENAI_API_KEY_HERE' with your actual API key!"
echo ""
echo "2. Ensure startup.sh is executable:"
echo "   chmod +x startup.sh"
echo ""
echo "3. Commit any remaining changes:"
echo "   git add ."
echo "   git commit -m 'Prepare for Azure deployment'"
echo ""
echo "4. Add Azure remote and deploy:"
echo "   git remote remove azure 2>/dev/null || true  # Remove old remote if exists"
echo "   git remote add azure $GIT_URL"
echo "   git push azure main"
echo ""
echo "5. Monitor deployment logs:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo ""
echo "6. Test your deployment:"
echo "   curl https://$APP_URL/"
echo "   curl https://$APP_URL/api/health"
echo "   open https://$APP_URL/docs"
echo ""
echo "========================================="
echo ""

# Ask if user wants to set environment variables now
read -p "Do you want to set environment variables now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    read -p "Enter your OpenAI API Key: " OPENAI_KEY
    
    if [ ! -z "$OPENAI_KEY" ]; then
        echo "Setting environment variables..."
        az webapp config appsettings set \
            --resource-group $RESOURCE_GROUP \
            --name $WEB_APP_NAME \
            --settings \
                OPENAI_API_KEY="$OPENAI_KEY" \
                OPENAI_MODEL='gpt-4-turbo-preview' \
                OPENAI_EMBEDDING_MODEL='text-embedding-3-small' \
                ENVIRONMENT='production' \
                LOG_LEVEL='INFO' \
                CORS_ORIGINS='*' \
            --output table
        print_success "Environment variables set successfully!"
    else
        print_warning "No API key provided. You'll need to set it manually later."
    fi
fi

echo ""
print_success "All done! Follow the next steps above to complete deployment."
echo ""
