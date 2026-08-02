using '../main.bicep'

param environmentName = 'prod'
param location = 'eastus'
param logAnalyticsWorkspaceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-prod/providers/Microsoft.OperationalInsights/workspaces/log-cch-prod'
param acrLoginServer = 'acrcchprod.azurecr.io'
param acrResourceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-prod/providers/Microsoft.ContainerRegistry/registries/acrcchprod'
param imageTag = 'prod-latest'
param keyVaultName = 'kv-cch-prod'
param userAssignedIdentityName = 'id-cch-backend-prod'
param enableExternalIngress = true
param customDomainName = 'api.cloudcontenthub.example'
param apiMinReplicas = 2
param apiMaxReplicas = 20
param workerMinReplicas = 2
param workerMaxReplicas = 30
