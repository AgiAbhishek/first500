# Azure Deployment Pre-Deployment Checklist

## ✅ Pre-Deployment Checklist

This checklist ensures your Azure deployment succeeds. Go through each item carefully.

### 1. Azure CLI Setup
- [ ] Azure CLI is installed (`az --version`)
- [ ] Logged into Azure (`az login`)
- [ ] Correct subscription is selected (`az account show`)

### 2. Environment Variables
Make sure you have the following ready:
- [ ] **OPENAI_API_KEY** - Your OpenAI API key
- [ ] **OPENAI_MODEL** - Model name (e.g., `gpt-4-turbo-preview`)
- [ ] **OPENAI_EMBEDDING_MODEL** - Embedding model (e.g., `text-embedding-3-small`)

### 3. Application Configuration Files

#### Required Files ✅
- [x] `runtime.txt` - Specifies Python version
- [x] `requirements.txt` - Python dependencies
- [x] `startup.sh` - Azure startup script
- [x] `.deployment` - Azure deployment config
- [x] `.azure-include` - Files to include in deployment

#### Configuration Files Status
All required files are present and configured correctly!

### 4. Common Deployment Failures & Solutions

#### Issue 1: "pip install failed"
**Solution:** Ensure all dependencies in `requirements.txt` are compatible with Python 3.11

#### Issue 2: "Application timeout"
**Solution:** The startup.sh includes `--timeout 600` for longer initialization

#### Issue 3: "Module not found"
**Solution:** Verify the app structure and that `app/main.py` exists

#### Issue 4: "Permission denied on startup.sh"
**Solution:** Make sure to set executable permissions before pushing:
```bash
chmod +x startup.sh
git add startup.sh
git commit -m "Add executable permissions to startup.sh"
```

#### Issue 5: "Vector store initialization failed"
**Solution:** Ensure `data/documents/` directory exists and contains documents

### 5. Deployment Steps

#### Step 1: Review Configuration
```bash
cd /Users/abhishekkushwaha/First500/ai-rag-agent

# Check all required files exist
ls -la runtime.txt requirements.txt startup.sh .deployment .azure-include
```

#### Step 2: Ensure startup.sh is executable
```bash
chmod +x startup.sh
```

#### Step 3: Commit all changes
```bash
git add .
git commit -m "Prepare for Azure deployment"
```

#### Step 4: Run deployment script
```bash
chmod +x deployment/azure/deploy.sh
./deployment/azure/deploy.sh
```

#### Step 5: Set environment variables
After the deployment script completes, it will provide a command like:
```bash
az webapp config appsettings set \
    --resource-group ai-rag-agent-rg \
    --name ai-rag-agent-xxxxxxxx \
    --settings \
        OPENAI_API_KEY='your_actual_key_here' \
        OPENAI_MODEL='gpt-4-turbo-preview' \
        OPENAI_EMBEDDING_MODEL='text-embedding-3-small' \
        ENVIRONMENT='production' \
        LOG_LEVEL='INFO' \
        CORS_ORIGINS='*'
```

**Replace** `your_actual_key_here` with your actual OpenAI API key!

#### Step 6: Deploy code via Git
```bash
# Add the Azure remote (use the GIT_URL from deployment script output)
git remote add azure <GIT_URL_FROM_DEPLOYMENT_SCRIPT>

# Push to Azure
git push azure main
```

#### Step 7: Monitor deployment
```bash
# Watch deployment logs in real-time
az webapp log tail \
    --resource-group ai-rag-agent-rg \
    --name ai-rag-agent-xxxxxxxx
```

#### Step 8: Test the deployment
```bash
# Replace with your actual app URL
curl https://ai-rag-agent-xxxxxxxx.azurewebsites.net/api/health

# Test the root endpoint
curl https://ai-rag-agent-xxxxxxxx.azurewebsites.net/
```

### 6. Post-Deployment Verification

- [ ] App responds to `/` endpoint
- [ ] App responds to `/api/health` endpoint
- [ ] App responds to `/docs` (FastAPI Swagger UI)
- [ ] Logs show no errors
- [ ] Can make a test query to `/api/ask`

### 7. Troubleshooting Commands

```bash
# View application logs
az webapp log tail --resource-group ai-rag-agent-rg --name <your-app-name>

# Check app settings
az webapp config appsettings list --resource-group ai-rag-agent-rg --name <your-app-name>

# Restart the app
az webapp restart --resource-group ai-rag-agent-rg --name <your-app-name>

# SSH into the container (for advanced debugging)
az webapp ssh --resource-group ai-rag-agent-rg --name <your-app-name>
```

### 8. Key Differences from Previous Deployment

> [!IMPORTANT]
> **Critical fixes in this deployment:**
> 1. **Startup script uses Gunicorn** - More stable for production
> 2. **Extended timeout (600s)** - Allows for vector store initialization
> 3. **Proper dependencies** - All required packages in requirements.txt
> 4. **Executable permissions** - startup.sh is marked as executable
> 5. **Build during deployment** - `.deployment` file enables Oryx build

## 🚀 Ready to Deploy?

Once you've checked all items above, run:
```bash
cd /Users/abhishekkushwaha/First500/ai-rag-agent
chmod +x deployment/azure/deploy.sh
./deployment/azure/deploy.sh
```

Then follow the output instructions to set environment variables and push your code!
