using '../main.bicep'

param environmentName = 'dev'
param location = 'eastus'
param logAnalyticsWorkspaceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-dev/providers/Microsoft.OperationalInsights/workspaces/log-cch-dev'
param acrLoginServer = 'acrcchdev.azurecr.io'
param acrResourceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-dev/providers/Microsoft.ContainerRegistry/registries/acrcchdev'
param imageTag = 'dev-latest'
param keyVaultName = 'kv-cch-dev'
param userAssignedIdentityName = 'id-cch-backend-dev'
param apiMinReplicas = 1
param apiMaxReplicas = 3
param workerMinReplicas = 1
param workerMaxReplicas = 5
