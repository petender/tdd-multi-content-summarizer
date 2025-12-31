targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Location for the OpenAI resource group')
@allowed(['australiaeast', 'canadaeast', 'eastus', 'eastus2', 'francecentral', 'japaneast', 'northcentralus', 'swedencentral', 'switzerlandnorth', 'uksouth', 'westeurope'])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAiLocation string

@description('OpenAI deployment name')
param openAiDeploymentName string = 'gpt-4o'

@description('OpenAI model name')
param openAiModelName string = 'gpt-4o'

@description('OpenAI model version')
param openAiModelVersion string = '2024-08-06'

@description('Id of the user or app to assign application roles')
param principalId string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var storageAccountNameRaw = replace('st${resourceToken}', '-', '')
var storageAccountName = length(storageAccountNameRaw) > 24 ? substring(storageAccountNameRaw, 0, 24) : storageAccountNameRaw
var tags = {
   'azd-env-name': environmentName
    SecurityControl: 'Ignore'
   }

// Resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    location: location
    tags: tags
    logAnalyticsName: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: '${abbrs.insightsComponents}${resourceToken}'
  }
}

// Storage for Azure Functions and caching
module storage './core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: storageAccountName
    location: location
    tags: tags
  }
}

// Cosmos DB for storing video metadata and summaries
module cosmos './core/database/cosmos/cosmos-account.bicep' = {
  name: 'cosmos'
  scope: rg
  params: {
    name: '${abbrs.documentDBDatabaseAccounts}${resourceToken}'
    location: location
    tags: tags
    databaseName: 'videosummaries'
    containers: [
      {
        name: 'videos'
        partitionKeyPath: '/userId'
      }
      {
        name: 'transcripts'
        partitionKeyPath: '/videoId'
      }
    ]
  }
}

// Azure OpenAI
module openAi './core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: openAiLocation
    tags: tags
    kind: 'OpenAI'
    sku: {
      name: 'S0'
    }
    deployments: [
      {
        name: openAiDeploymentName
        model: {
          format: 'OpenAI'
          name: openAiModelName
          version: openAiModelVersion
        }
        sku: {
          name: 'Standard'
          capacity: 30
        }
      }
    ]
  }
}

// Azure Functions for backend processing
module functions './core/host/functions.bicep' = {
  name: 'functions'
  scope: rg
  params: {
    name: '${abbrs.webSitesFunctions}${resourceToken}'
    location: location
    tags: tags
    storageAccountName: storage.outputs.name
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    appSettings: {
      AZURE_OPENAI_ENDPOINT: openAi.outputs.endpoint
      AZURE_OPENAI_DEPLOYMENT_NAME: openAiDeploymentName
      COSMOS_ENDPOINT: cosmos.outputs.endpoint
      COSMOS_DATABASE_NAME: 'videosummaries'
      COSMOS_CONTAINER_VIDEOS: 'videos'
      COSMOS_CONTAINER_TRANSCRIPTS: 'transcripts'
    }
    runtimeName: 'python'
    runtimeVersion: '3.11'
  }
}

// Static Web App for frontend
module web './core/host/appservice.bicep' = {
  name: 'web'
  scope: rg
  params: {
    name: '${abbrs.webSitesAppService}${resourceToken}'
    location: location
    tags: tags
    apiUrl: '${functions.outputs.uri}/api'
  }
}

// Role assignments for Function App managed identity
module functionsStorageRole './core/security/role.bicep' = {
  scope: rg
  name: 'functions-storage-role'
  params: {
    principalId: functions.outputs.principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' // Storage Blob Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module functionsStorageTableRole './core/security/role.bicep' = {
  scope: rg
  name: 'functions-storage-table-role'
  params: {
    principalId: functions.outputs.principalId
    roleDefinitionId: '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3' // Storage Table Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module functionsOpenAiRole './core/security/role.bicep' = {
  scope: rg
  name: 'functions-openai-role'
  params: {
    principalId: functions.outputs.principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    principalType: 'ServicePrincipal'
  }
}

module functionsCosmosRole './core/security/role.bicep' = {
  scope: rg
  name: 'functions-cosmos-role'
  params: {
    principalId: functions.outputs.principalId
    roleDefinitionId: 'b24988ac-6180-42a0-ab88-20f7382dd24c' // Cosmos DB Contributor
    principalType: 'ServicePrincipal'
  }
}

// Role assignments for user
module openAiRoleUser './core/security/role.bicep' = if (!empty(principalId)) {
  scope: rg
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    principalType: 'User'
  }
}

module cosmosRoleUser './core/security/role.bicep' = if (!empty(principalId)) {
  scope: rg
  name: 'cosmos-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'b24988ac-6180-42a0-ab88-20f7382dd24c' // Cosmos DB Contributor
    principalType: 'User'
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name

output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_DEPLOYMENT_NAME string = openAiDeploymentName

output COSMOS_ENDPOINT string = cosmos.outputs.endpoint
output COSMOS_DATABASE_NAME string = 'videosummaries'

output FUNCTIONS_APP_NAME string = functions.outputs.name
output FUNCTIONS_URI string = functions.outputs.uri

output APPSERVICE_NAME string = web.outputs.name
output APPSERVICE_URI string = web.outputs.uri
