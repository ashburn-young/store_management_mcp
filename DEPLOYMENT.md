# Deployment Guide

This guide walks you through deploying the Store Management MCP Servers to Azure.

## Prerequisites

1. **Azure CLI** - [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Developer CLI (azd)** - [Install azd](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
3. **Docker Desktop** - [Install Docker](https://www.docker.com/products/docker-desktop)
4. **Azure Subscription** with permissions to create resources
5. **Google Cloud Platform** account with Business Profile API access

## Step 1: Clone and Setup

```bash
git clone https://github.com/ashburn-young/store_management_mcp.git
cd store_management_mcp
```

## Step 2: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```bash
   # Azure Configuration
   AZURE_ENV_NAME=your-environment-name
   AZURE_LOCATION=eastus
   AZURE_SUBSCRIPTION_ID=your-subscription-id

   # Azure OpenAI (Optional but recommended)
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   AZURE_OPENAI_API_VERSION=2024-02-01

   # Google API Configuration
   GOOGLE_API_KEY=your-google-api-key
   GOOGLE_SERVICE_ACCOUNT_JSON=your-service-account-json
   ```

## Step 3: Google Cloud Setup

### Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the "My Business Business Information API" and "My Business Business Calls API"
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Give it a name and description
   - Grant necessary permissions
   - Download the JSON key file

### Set Environment Variables
```bash
# Set the API key
export GOOGLE_API_KEY="your-api-key-here"

# Set the service account JSON (as a string)
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

## Step 4: Azure OpenAI Setup (Optional)

1. Create Azure OpenAI resource:
   ```bash
   az cognitiveservices account create \
     --name "your-openai-resource" \
     --resource-group "your-resource-group" \
     --kind "OpenAI" \
     --sku "S0" \
     --location "eastus" \
     --yes
   ```

2. Deploy a model:
   ```bash
   # Deploy GPT-4o model
   az cognitiveservices account deployment create \
     --resource-group "your-resource-group" \
     --name "your-openai-resource" \
     --deployment-name "gpt-4o" \
     --model-name "gpt-4o" \
     --model-version "2024-02-01" \
     --model-format "OpenAI" \
     --sku-capacity 10
   ```

## Step 5: Deploy to Azure

### Using Azure Developer CLI (Recommended)

1. **Login to Azure**:
   ```bash
   azd auth login
   az login
   ```

2. **Initialize the project**:
   ```bash
   azd init
   ```

3. **Deploy everything**:
   ```bash
   azd up
   ```

   This will:
   - Create all Azure resources (Container Apps, Key Vault, Storage, etc.)
   - Build and push Docker images
   - Deploy the services
   - Configure environment variables and secrets

4. **Access your deployment**:
   ```bash
   azd show
   ```

### Manual Deployment

If you prefer manual deployment:

1. **Create resource group**:
   ```bash
   az group create --name store-management-rg --location eastus
   ```

2. **Deploy infrastructure**:
   ```bash
   az deployment group create \
     --resource-group store-management-rg \
     --template-file infra/main.bicep \
     --parameters @infra/main.parameters.json
   ```

3. **Build and push images**:
   ```bash
   # Get ACR login server
   ACR_LOGIN_SERVER=$(az acr show --name your-acr-name --query loginServer --output tsv)
   
   # Login to ACR
   az acr login --name your-acr-name
   
   # Build and push images
   docker build -f Dockerfile.dashboard -t $ACR_LOGIN_SERVER/dashboard:latest .
   docker build -f Dockerfile.collection -t $ACR_LOGIN_SERVER/collection:latest .
   docker build -f Dockerfile.aggregation -t $ACR_LOGIN_SERVER/aggregation:latest .
   
   docker push $ACR_LOGIN_SERVER/dashboard:latest
   docker push $ACR_LOGIN_SERVER/collection:latest
   docker push $ACR_LOGIN_SERVER/aggregation:latest
   ```

4. **Update container apps**:
   ```bash
   az containerapp update --name dashboard --resource-group store-management-rg --image $ACR_LOGIN_SERVER/dashboard:latest
   az containerapp update --name collection --resource-group store-management-rg --image $ACR_LOGIN_SERVER/collection:latest
   az containerapp update --name aggregation --resource-group store-management-rg --image $ACR_LOGIN_SERVER/aggregation:latest
   ```

## Step 6: Verify Deployment

1. **Check service status**:
   ```bash
   az containerapp list --resource-group store-management-rg --query "[].{Name:name, Status:properties.runningStatus}" --output table
   ```

2. **Get service URLs**:
   ```bash
   az containerapp list --resource-group store-management-rg --query "[].{Name:name, URL:properties.configuration.ingress.fqdn}" --output table
   ```

3. **View logs**:
   ```bash
   az containerapp logs show --name dashboard --resource-group store-management-rg --follow
   ```

## Step 7: Configure Production Settings

1. **Set up monitoring**:
   - Enable Application Insights
   - Set up log analytics
   - Configure alerts

2. **Security hardening**:
   - Review Key Vault access policies
   - Configure network security groups
   - Enable managed identity

3. **Scaling configuration**:
   - Set appropriate min/max replicas
   - Configure CPU/memory limits
   - Set up autoscaling rules

## Troubleshooting

### Common Issues

1. **Docker build fails**:
   - Ensure Docker Desktop is running
   - Check Dockerfile syntax
   - Verify all dependencies are in requirements.txt

2. **Container app won't start**:
   - Check environment variables are set correctly
   - Verify Key Vault permissions
   - Review container logs

3. **Google API errors**:
   - Verify API key is correct
   - Check service account permissions
   - Ensure APIs are enabled in Google Cloud

4. **Azure OpenAI connection fails**:
   - Verify endpoint URL is correct
   - Check deployment name matches
   - Ensure Azure CLI is authenticated

### Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review Azure Container Apps documentation
- Check Google Business Profile API documentation
- Open an issue on GitHub for project-specific problems

## Cost Optimization

- Use consumption-based pricing for Container Apps
- Set appropriate scaling limits
- Monitor resource usage with Azure Monitor
- Consider using Azure reservations for long-term deployments

## Security Best Practices

- Store all secrets in Azure Key Vault
- Use managed identities for Azure service authentication
- Enable TLS for all endpoints
- Regularly rotate API keys and secrets
- Monitor access logs and set up alerts
