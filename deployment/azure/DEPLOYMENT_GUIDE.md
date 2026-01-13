# 🚀 Azure Deployment Guide - AI RAG Agent

This guide will help you successfully deploy your AI RAG Agent to Azure App Service.

## ⚠️ Critical Success Factors

Based on your validation results, here's what you need to ensure:

### 1. Install Azure CLI (REQUIRED)

Azure CLI is not currently installed. Install it first:

**For macOS:**
```bash
brew update && brew install azure-cli
```

**Verify installation:**
```bash
az --version
```

### 2. Commit Your Changes

You have uncommitted changes. Commit them before deploying:

```bash
cd /Users/abhishekkushwaha/First500/ai-rag-agent
git add .
git commit -m "Prepare for Azure deployment with improved scripts"
```

### 3. Prepare Your OpenAI API Key

You'll need your OpenAI API key ready. Make sure it starts with `sk-`.

---

## 📋 Step-by-Step Deployment Process

### Step 1: Install Prerequisites

```bash
# Install Azure CLI (if not already done)
brew update && brew install azure-cli

# Verify installation
az --version

# Login to Azure
az login
```

### Step 2: Validate Your Setup

```bash
cd /Users/abhishekkushwaha/First500/ai-rag-agent
./deployment/azure/validate-deployment.sh
```

This should show all green checkmarks. If not, fix any issues before proceeding.

### Step 3: Run the Deployment Script

We've created an improved deployment script with better error handling:

```bash
./deployment/azure/deploy-improved.sh
```

The script will:
- ✅ Create a resource group in Azure
- ✅ Create an App Service Plan (B1 tier)
- ✅ Create a Web App with Python 3.11 runtime
- ✅ Configure startup command
- ✅ Enable application logging
- ✅ Set up Git deployment
- ✅ Optionally set environment variables

### Step 4: Set Environment Variables

**Option A: During deployment (recommended)**

When the deployment script asks "Do you want to set environment variables now?", answer `y` and provide your OpenAI API key.

**Option B: Manually after deployment**

If you skipped it during deployment, run this command (replace the placeholders):

```bash
az webapp config appsettings set \
    --resource-group ai-rag-agent-rg \
    --name <YOUR_WEB_APP_NAME> \
    --settings \
        OPENAI_API_KEY='sk-your-actual-key-here' \
        OPENAI_MODEL='gpt-4-turbo-preview' \
        OPENAI_EMBEDDING_MODEL='text-embedding-3-small' \
        ENVIRONMENT='production' \
        LOG_LEVEL='INFO' \
        CORS_ORIGINS='*'
```

### Step 5: Deploy Your Code

After the deployment script completes, it will provide a Git URL. Use it to push your code:

```bash
# Remove old Azure remote if it exists
git remote remove azure 2>/dev/null || true

# Add the new Azure remote (use the URL from deployment script output)
git remote add azure <GIT_URL_FROM_DEPLOYMENT_SCRIPT>

# Push to Azure
git push azure main
```

**Example:**
```bash
git remote add azure https://ai-rag-agent-1234567890.scm.azurewebsites.net/ai-rag-agent-1234567890.git
git push azure main
```

### Step 6: Monitor Deployment

Watch the deployment logs in real-time:

```bash
az webapp log tail \
    --resource-group ai-rag-agent-rg \
    --name <YOUR_WEB_APP_NAME>
```

Look for these success indicators:
- ✅ "Dependencies installed successfully!"
- ✅ "Vector store initialized successfully"
- ✅ "API running in production mode"
- ✅ Gunicorn workers starting

### Step 7: Test Your Deployment

```bash
# Replace with your actual app URL
APP_URL="<YOUR_APP_NAME>.azurewebsites.net"

# Test root endpoint
curl https://$APP_URL/

# Test health endpoint
curl https://$APP_URL/api/health

# Open API documentation in browser
open https://$APP_URL/docs
```

### Step 8: Test the RAG Functionality

```bash
# Test asking a question
curl -X POST https://$APP_URL/api/ask \
    -H "Content-Type: application/json" \
    -d '{
        "question": "What is this system about?",
        "session_id": "test-123"
    }'
```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "pip install failed"

**Symptoms:** Deployment fails during `pip install`

**Solution:**
```bash
# Check requirements.txt for incompatible versions
cat requirements.txt

# Try deploying again - Azure sometimes has transient issues
git push azure main --force
```

### Issue 2: "Application timeout" or "Container didn't respond"

**Symptoms:** App doesn't start or shows 503 errors

**Solution:**
```bash
# Check the logs
az webapp log tail --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>

# Restart the app
az webapp restart --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>

# Verify startup.sh has correct timeout
cat startup.sh  # Should show --timeout 600
```

### Issue 3: "Module not found" errors

**Symptoms:** Logs show `ModuleNotFoundError`

**Solution:**
```bash
# Ensure all imports in app/main.py are correct
# Verify app structure matches Python import paths
# Check that __init__.py files exist where needed

# Force rebuild
az webapp restart --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
```

### Issue 4: "Vector store initialization failed"

**Symptoms:** App starts but can't retrieve documents

**Solution:**
```bash
# Verify documents directory is included in deployment
cat .azure-include  # Should include data/documents/

# Check if documents exist
ls -la data/documents/

# Re-deploy if needed
git push azure main --force
```

### Issue 5: "OpenAI API error"

**Symptoms:** 401 or 403 errors when asking questions

**Solution:**
```bash
# Verify API key is set correctly
az webapp config appsettings list \
    --resource-group ai-rag-agent-rg \
    --name <YOUR_APP_NAME> \
    --query "[?name=='OPENAI_API_KEY']"

# Set it again if needed
az webapp config appsettings set \
    --resource-group ai-rag-agent-rg \
    --name <YOUR_APP_NAME> \
    --settings OPENAI_API_KEY='sk-your-actual-key'
```

---

## 📊 Monitoring and Maintenance

### View Logs
```bash
# Stream logs in real-time
az webapp log tail --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>

# Download logs
az webapp log download --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
```

### Restart Application
```bash
az webapp restart --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
```

### Update Environment Variables
```bash
az webapp config appsettings set \
    --resource-group ai-rag-agent-rg \
    --name <YOUR_APP_NAME> \
    --settings KEY='value'
```

### Scale Up/Down
```bash
# Scale to a higher tier for better performance
az appservice plan update \
    --resource-group ai-rag-agent-rg \
    --name ai-rag-agent-plan \
    --sku S1

# Scale back down to save costs
az appservice plan update \
    --resource-group ai-rag-agent-rg \
    --name ai-rag-agent-plan \
    --sku B1
```

---

## 🎯 Quick Start (After First Setup)

For subsequent deployments, you only need:

```bash
# 1. Make your changes
# 2. Commit them
git add .
git commit -m "Your changes"

# 3. Push to Azure
git push azure main

# 4. Monitor
az webapp log tail --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
```

---

## ✅ Success Checklist

- [ ] Azure CLI installed and logged in
- [ ] All files committed to Git
- [ ] Deployment script ran successfully
- [ ] Environment variables set (especially OPENAI_API_KEY)
- [ ] Code pushed to Azure via Git
- [ ] App responds to `/` endpoint
- [ ] App responds to `/api/health` endpoint
- [ ] Swagger UI accessible at `/docs`
- [ ] Can successfully query `/api/ask` endpoint
- [ ] Logs show no errors

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. **Check deployment logs:**
   ```bash
   az webapp log tail --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
   ```

2. **SSH into the container:**
   ```bash
   az webapp ssh --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
   ```

3. **View detailed diagnostics:**
   - Go to Azure Portal → Your App Service → Diagnose and solve problems

4. **Check Azure Service Health:**
   - Ensure Azure services are operational in your region

---

## 🎉 After Successful Deployment

Once deployed successfully:

1. **Save your app URL** for easy access
2. **Test all API endpoints** thoroughly
3. **Monitor initial usage** for any issues
4. **Consider setting up:**
   - Custom domain name
   - SSL certificate (if not using *.azurewebsites.net)
   - Application Insights for monitoring
   - CI/CD with GitHub Actions

Congratulations! Your AI RAG Agent is now live on Azure! 🚀
