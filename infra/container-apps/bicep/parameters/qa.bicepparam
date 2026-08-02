using '../main.bicep'

param environmentName = 'qa'
param location = 'eastus'
param logAnalyticsWorkspaceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-qa/providers/Microsoft.OperationalInsights/workspaces/log-cch-qa'
param acrLoginServer = 'acrcchqa.azurecr.io'
param acrResourceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-qa/providers/Microsoft.ContainerRegistry/registries/acrcchqa'
param imageTag = 'qa-latest'
param keyVaultName = 'kv-cch-qa'
param userAssignedIdentityName = 'id-cch-backend-qa'
param apiMinReplicas = 1
param apiMaxReplicas = 5
param workerMinReplicas = 1
param workerMaxReplicas = 10
