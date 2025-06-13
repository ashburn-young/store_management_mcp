/*
  Azure Bicep Deployment for Google Business Analytics MCP Solution

  Prerequisites:
    - Azure subscription with Container Apps, Key Vault, OpenAI, and ACR enabled
    - Sufficient quota for OpenAI and Container Apps
    - Contributor or Owner role for deployment

  Deployment:
    az deployment group create --resource-group <rg> --template-file azure_deployment_example.bicep --parameters ...

  Best Practices:
    - Parameterize all container images and secrets for easy updates
    - Use Key Vault for all secrets (including OpenAI keys if possible)
    - For production, consider private networking and disabling public endpoints
    - Ensure all health probe endpoints are implemented in your containers
    - Monitor and adjust scaling rules based on real usage
    - Tag resources for cost management and governance
*/

// Azure Deployment Template for Google Business Analytics MCP Servers
// This Bicep template deploys the complete infrastructure for hosting the MCP servers in Azure

@description('The environment name (e.g., dev, staging, prod)')
param environmentName string = 'prod'

@description('The primary location for all resources')
param location string = resourceGroup().location

@description('The name of the Azure OpenAI service')
param openAiServiceName string = 'openai-${environmentName}-${uniqueString(resourceGroup().id)}'

@description('The SKU name for Azure OpenAI service')
param openAiSkuName string = 'S0'

@description('Model deployments for Azure OpenAI')
param modelDeployments array = [
  {
    name: 'gpt-4o'
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
    sku: {
      name: 'Standard'
      capacity: 10
    }
  }
  {
    name: 'text-embedding-ada-002'
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    sku: {
      name: 'Standard'
      capacity: 10
    }
  }
]

@description('Container image for the collection agent')
param collectionAgentImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Container image for the aggregation agent')
param aggregationAgentImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Google API key for business profile access')
@secure()
param googleApiKey string

@description('Google service account JSON content')
@secure()
param googleServiceAccountJson string

// Variables
var resourcePrefix = 'gba-${environmentName}'
var tags = {
  Environment: environmentName
  Application: 'GoogleBusinessAnalytics'
  'Cost Center': 'Analytics'
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${resourcePrefix}-logs'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${resourcePrefix}-insights'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Key Vault for secure storage of secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${resourcePrefix}-kv'
  location: location
  tags: tags
  properties: {
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    tenantId: tenant().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    accessPolicies: []
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// Store Google API key in Key Vault
resource googleApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'google-api-key'
  properties: {
    value: googleApiKey
  }
}

// Store Google service account JSON in Key Vault
resource googleServiceAccountSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'google-service-account-json'
  properties: {
    value: googleServiceAccountJson
  }
}

// Azure OpenAI Service
resource openAiService 'Microsoft.CognitiveServices/accounts@2024-06-01-preview' = {
  name: openAiServiceName
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: openAiSkuName
  }
  properties: {
    customSubDomainName: openAiServiceName
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// Deploy models to Azure OpenAI
resource openAiModelDeployments 'Microsoft.CognitiveServices/accounts/deployments@2024-06-01-preview' = [for deployment in modelDeployments: {
  parent: openAiService
  name: deployment.name
  properties: {
    model: deployment.model
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    currentCapacity: deployment.sku.capacity
    raiPolicyName: 'Microsoft.Default'
  }
  sku: deployment.sku
}]

// Storage Account for data persistence
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: '${replace(resourcePrefix, '-', '')}storage'
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

// Blob containers for different data types
resource dataContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for containerName in ['processed-data', 'snapshots', 'raw-data', 'backups']: {
  name: '${storageAccount.name}/default/${containerName}'
  properties: {
    publicAccess: 'None'
  }
}]

// User-assigned managed identity for Container Apps
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${resourcePrefix}-identity'
  location: location
  tags: tags
}

// Role assignments for the managed identity
resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, userAssignedIdentity.id, '4633458b-17de-408a-b874-0445c86b69e6')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource cognitiveServicesUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: openAiService
  name: guid(openAiService.id, userAssignedIdentity.id, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908') // Cognitive Services User
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource storageBlobDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, userAssignedIdentity.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${resourcePrefix}-env'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    infrastructureResourceGroup: '${resourceGroup().name}-infrastructure'
  }
}

// Collection Agent Container App
resource collectionAgentApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-collection-agent'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      secrets: [
        {
          name: 'google-api-key'
          keyVaultUrl: googleApiKeySecret.properties.secretUri
          identity: userAssignedIdentity.id
        }
        {
          name: 'google-service-account-json'
          keyVaultUrl: googleServiceAccountSecret.properties.secretUri
          identity: userAssignedIdentity.id
        }
        {
          name: 'azure-openai-api-key'
          value: openAiService.listKeys().key1
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'collection-agent'
          image: collectionAgentImage
          env: [
            {
              name: 'GOOGLE_API_KEY'
              secretRef: 'google-api-key'
            }
            {
              name: 'GOOGLE_SERVICE_ACCOUNT_JSON'
              secretRef: 'google-service-account-json'
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openAiService.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'azure-openai-api-key'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: modelDeployments[0].name
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: '2024-08-01-preview'
            }
            {
              name: 'STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsights.properties.ConnectionString
            }
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
          ]
          resources: {
            cpu: 1
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 30
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/ready'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
        rules: [
          {
            name: 'cpu-scaling'
            custom: {
              type: 'cpu'
              metadata: {
                type: 'Utilization'
                value: '70'
              }
            }
          }
          {
            name: 'memory-scaling'
            custom: {
              type: 'memory'
              metadata: {
                type: 'Utilization'
                value: '80'
              }
            }
          }
        ]
      }
    }
  }
}

// Aggregation Agent Container App
resource aggregationAgentApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-aggregation-agent'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8001
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      secrets: [
        {
          name: 'azure-openai-api-key'
          value: openAiService.listKeys().key1
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'aggregation-agent'
          image: aggregationAgentImage
          env: [
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openAiService.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'azure-openai-api-key'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: modelDeployments[0].name
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: '2024-08-01-preview'
            }
            {
              name: 'STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsights.properties.ConnectionString
            }
            {
              name: 'COLLECTION_AGENT_ENDPOINT'
              value: 'https://${collectionAgentApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
          ]
          resources: {
            cpu: 1
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8001
              }
              initialDelaySeconds: 30
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/ready'
                port: 8001
              }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'cpu-scaling'
            custom: {
              type: 'cpu'
              metadata: {
                type: 'Utilization'
                value: '70'
              }
            }
          }
        ]
      }
    }
  }
}

// Dashboard Container App (Streamlit)
resource dashboardApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-dashboard'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8501
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'dashboard'
          image: 'your-registry.azurecr.io/dashboard:latest' // Replace with your dashboard image
          env: [
            {
              name: 'STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'COLLECTION_AGENT_ENDPOINT'
              value: 'https://${collectionAgentApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'AGGREGATION_AGENT_ENDPOINT'
              value: 'https://${aggregationAgentApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: applicationInsights.properties.ConnectionString
            }
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
          ]
          resources: {
            cpu: 1
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// Azure Container Registry (optional, for custom images)
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: '${padRight(replace(resourcePrefix, '-', ''), 5, 'x')}acr'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

// Grant Container Apps pull access to ACR
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, userAssignedIdentity.id, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output resourceGroupName string = resourceGroup().name
output openAiEndpoint string = openAiService.properties.endpoint
output openAiServiceName string = openAiService.name
output keyVaultName string = keyVault.name
output storageAccountName string = storageAccount.name
output collectionAgentUrl string = 'https://${collectionAgentApp.properties.configuration.ingress.fqdn}'
output aggregationAgentUrl string = 'https://${aggregationAgentApp.properties.configuration.ingress.fqdn}'
output dashboardUrl string = 'https://${dashboardApp.properties.configuration.ingress.fqdn}'
output containerRegistryName string = containerRegistry.name
output applicationInsightsName string = applicationInsights.name
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.name
output managedIdentityId string = userAssignedIdentity.id
output managedIdentityClientId string = userAssignedIdentity.properties.clientId
