# 🚀 Quick Deployment Commands

## First Time Deployment

```bash
# 1. Install Azure CLI (once)
brew update && brew install azure-cli

# 2. Login to Azure (once)
az login

# 3. Navigate to project
cd /Users/abhishekkushwaha/First500/ai-rag-agent

# 4. Commit changes
git add .
git commit -m "Prepare for Azure deployment"

# 5. Validate setup
./deployment/azure/validate-deployment.sh

# 6. Run deployment
./deployment/azure/deploy-improved.sh

# 7. When prompted, enter your OpenAI API key

# 8. After deployment completes, push code
git remote add azure <GIT_URL_FROM_OUTPUT>
git push azure main

# 9. Monitor deployment
az webapp log tail --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
```

## Update Existing Deployment

```bash
cd /Users/abhishekkushwaha/First500/ai-rag-agent

git add .
git commit -m "Update application"
git push azure main

az webapp log tail --resource-group ai-rag-agent-rg --name <YOUR_APP_NAME>
```

## Common Commands

```bash
# View logs
az webapp log tail --resource-group ai-rag-agent-rg --name <APP_NAME>

# Restart app
az webapp restart --resource-group ai-rag-agent-rg --name <APP_NAME>

# Update API key
az webapp config appsettings set \
    --resource-group ai-rag-agent-rg \
    --name <APP_NAME> \
    --settings OPENAI_API_KEY='sk-your-key'

# Test deployment
curl https://<APP_NAME>.azurewebsites.net/
curl https://<APP_NAME>.azurewebsites.net/api/health
open https://<APP_NAME>.azurewebsites.net/docs
```

## Emergency Rollback

```bash
# If deployment fails, restart the app
az webapp restart --resource-group ai-rag-agent-rg --name <APP_NAME>

# Or delete and redeploy
az webapp delete --resource-group ai-rag-agent-rg --name <APP_NAME>
./deployment/azure/deploy-improved.sh
```
