#!/bin/bash

# Azure App Service Deployment Script for AI RAG Agent
# This script deploys the application to Azure App Service

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="ai-rag-agent-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="ai-rag-agent-plan"
WEB_APP_NAME="ai-rag-agent-$(date +%s)"  # Unique name with timestamp
RUNTIME="PYTHON:3.11"

echo "========================================="
echo "AI RAG Agent - Azure Deployment"
echo "========================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
echo "Checking Azure login status..."
az account show &> /dev/null || {
    echo "Not logged in to Azure. Please login:"
    az login
}

# Get subscription info
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "Using subscription: $SUBSCRIPTION_NAME"

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

# Create App Service Plan (Basic tier for production, Free tier for testing)
echo "Creating App Service Plan: $APP_SERVICE_PLAN..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux \
    --output table

# Create Web App
echo "Creating Web App: $WEB_APP_NAME..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --runtime $RUNTIME \
    --output table

# Configure environment variables
echo "Configuring environment variables..."
echo "⚠️  Please set your OpenAI API key and other secrets manually:"
echo ""
echo "az webapp config appsettings set \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --name $WEB_APP_NAME \\"
echo "    --settings \\"
echo "        OPENAI_API_KEY='your_key_here' \\"
echo "        ENVIRONMENT='production' \\"
echo "        LOG_LEVEL='INFO' \\"
echo "        CORS_ORIGINS='*'"
echo ""

# Set startup command
echo "Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --startup-file "uvicorn app.main:app --host 0.0.0.0 --port 8000" \
    --output table

# Enable logging
echo "Enabling application logging..."
az webapp log config \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --application-logging filesystem \
    --level information \
    --output table

# Deploy from local Git (optional - can also use GitHub Actions)
echo "Setting up local Git deployment..."
az webapp deployment source config-local-git \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --output table

# Get deployment URL
GIT_URL=$(az webapp deployment source show \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query repositoryUrl -o tsv)

# Get app URL
APP_URL=$(az webapp show \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query defaultHostName -o tsv)

echo ""
echo "========================================="
echo "✓ Deployment Configuration Complete!"
echo "========================================="
echo ""
echo "Web App Name: $WEB_APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "App URL: https://$APP_URL"
echo "Git URL: $GIT_URL"
echo ""
echo "Next Steps:"
echo "1. Set environment variables (see command above)"
echo "2. Deploy your code:"
echo "   cd /Users/abhishekkushwaha/First500/ai-rag-agent"
echo "   git remote add azure $GIT_URL"
echo "   git push azure main"
echo ""
echo "3. View logs:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo ""
echo "4. Test your API:"
echo "   curl https://$APP_URL/api/health"
echo "========================================="
