targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Google API Key for accessing Google Business Profile API')
@secure()
param googleApiKey string = ''

@description('Google Service Account JSON for authentication')
@secure()
param googleServiceAccountJson string = ''

@description('Flag to enable Azure OpenAI integration')
param enableAzureOpenAI bool = true

// Generate a unique resource token (shortened for name length limits)
var resourceToken = toLower(take(uniqueString(subscription().id, resourceGroup().id, environmentName), 8))
var resourcePrefix = '${take(environmentName, 10)}-${resourceToken}'

// Tags for all resources
var tags = {
  'azd-env-name': environmentName
  Environment: environmentName
  Application: 'GoogleBusinessAnalytics'
  Purpose: 'MCP-Servers'
}

// Log Analytics Workspace for monitoring
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

// Application Insights for monitoring
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

// Container Registry for storing container images
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${replace(resourcePrefix, '-', '')}registry'
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

// Key Vault for storing secrets
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

// User-assigned managed identity for the container apps
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${resourcePrefix}-identity'
  location: location
  tags: tags
}

// Azure OpenAI Service (conditionally deployed)
resource openAiService 'Microsoft.CognitiveServices/accounts@2024-10-01' = if (enableAzureOpenAI) {
  name: '${resourcePrefix}-openai'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${resourcePrefix}-openai'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// Deploy GPT-4o model
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-06-01-preview' = if (enableAzureOpenAI) {
  parent: openAiService
  name: 'gpt-4o'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
    currentCapacity: 10
    raiPolicyName: 'Microsoft.Default'
  }
  sku: {
    name: 'Standard'
    capacity: 10
  }
}

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

// Storage containers
resource dataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storageAccount.name}/default/data'
  properties: {
    publicAccess: 'None'
  }
}

resource snapshotsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storageAccount.name}/default/snapshots'
  properties: {
    publicAccess: 'None'
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
  }
}

// Store secrets in Key Vault if provided
resource googleApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(googleApiKey)) {
  parent: keyVault
  name: 'google-api-key'
  properties: {
    value: googleApiKey
  }
}

resource googleServiceAccountSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(googleServiceAccountJson)) {
  parent: keyVault
  name: 'google-service-account-json'
  properties: {
    value: googleServiceAccountJson
  }
}

// Role assignments for the managed identity
resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, userAssignedIdentity.id, '4633458b-17de-408a-b874-0445c86b69e6')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource storageDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, userAssignedIdentity.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, userAssignedIdentity.id, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource openAiUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableAzureOpenAI) {
  name: guid(openAiService.id, userAssignedIdentity.id, '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
  scope: openAiService
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd') // Cognitive Services OpenAI User
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Collection Agent Container App
resource collectionAgentApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-collection'
  location: location
  tags: union(tags, {
    'azd-service-name': 'collection-agent'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['*']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: userAssignedIdentity.id
        }
      ]
      secrets: [
        {
          name: 'google-api-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/google-api-key'
          identity: userAssignedIdentity.id
        }
        {
          name: 'google-service-account-json'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/google-service-account-json'
          identity: userAssignedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'collection-agent'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
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
              name: 'AZURE_STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'AZURE_STORAGE_CONTAINER_NAME'
              value: 'data'
            }
            {
              name: 'AZURE_KEY_VAULT_URL'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: enableAzureOpenAI ? openAiService.properties.endpoint : ''
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: '2024-02-01'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: 'gpt-4o'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedIdentity.properties.clientId
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 30
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
  dependsOn: [
    keyVaultSecretsUserRole
    storageDataContributorRole
    acrPullRole
    openAiUserRole
  ]
}

// Aggregation Agent Container App
resource aggregationAgentApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-aggregation'
  location: location
  tags: union(tags, {
    'azd-service-name': 'aggregation-agent'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8001
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['*']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: userAssignedIdentity.id
        }
      ]
      secrets: [
        {
          name: 'google-api-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/google-api-key'
          identity: userAssignedIdentity.id
        }
        {
          name: 'google-service-account-json'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/google-service-account-json'
          identity: userAssignedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'aggregation-agent'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
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
              name: 'AZURE_STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'AZURE_STORAGE_CONTAINER_NAME'
              value: 'snapshots'
            }
            {
              name: 'AZURE_KEY_VAULT_URL'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: enableAzureOpenAI ? openAiService.properties.endpoint : ''
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: '2024-02-01'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: 'gpt-4o'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedIdentity.properties.clientId
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8001
              }
              initialDelaySeconds: 30
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
  dependsOn: [
    keyVaultSecretsUserRole
    storageDataContributorRole
    acrPullRole
    openAiUserRole
  ]
}

// Dashboard Container App
resource dashboardApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${resourcePrefix}-dashboard'
  location: location
  tags: union(tags, {
    'azd-service-name': 'dashboard'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8501
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['*']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: userAssignedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'dashboard'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'COLLECTION_AGENT_URL'
              value: 'https://${collectionAgentApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'AGGREGATION_AGENT_URL'
              value: 'https://${aggregationAgentApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedIdentity.properties.clientId
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/_stcore/health'
                port: 8501
              }
              initialDelaySeconds: 30
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup().name
output RESOURCE_GROUP_ID string = resourceGroup().id

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.properties.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.name

output AZURE_KEY_VAULT_ENDPOINT string = keyVault.properties.vaultUri
output AZURE_KEY_VAULT_NAME string = keyVault.name

output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_STORAGE_ACCOUNT_ENDPOINT string = storageAccount.properties.primaryEndpoints.blob

output AZURE_OPENAI_ENDPOINT string = enableAzureOpenAI ? openAiService.properties.endpoint : ''
output AZURE_OPENAI_NAME string = enableAzureOpenAI ? openAiService.name : ''

output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = containerAppsEnvironment.name
output AZURE_CONTAINER_APPS_ENVIRONMENT_ID string = containerAppsEnvironment.id

output COLLECTION_AGENT_URL string = 'https://${collectionAgentApp.properties.configuration.ingress.fqdn}'
output AGGREGATION_AGENT_URL string = 'https://${aggregationAgentApp.properties.configuration.ingress.fqdn}'
output DASHBOARD_URL string = 'https://${dashboardApp.properties.configuration.ingress.fqdn}'

output SERVICE_COLLECTION_AGENT_IDENTITY_PRINCIPAL_ID string = userAssignedIdentity.properties.principalId
output SERVICE_COLLECTION_AGENT_NAME string = collectionAgentApp.name
output SERVICE_AGGREGATION_AGENT_NAME string = aggregationAgentApp.name
output SERVICE_DASHBOARD_NAME string = dashboardApp.name
