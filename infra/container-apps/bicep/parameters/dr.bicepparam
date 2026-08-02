using '../main.bicep'

param environmentName = 'dr'
param location = 'westus2'
param logAnalyticsWorkspaceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-dr/providers/Microsoft.OperationalInsights/workspaces/log-cch-dr'
param acrLoginServer = 'acrcchprod.azurecr.io'
param acrResourceId = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-cch-prod/providers/Microsoft.ContainerRegistry/registries/acrcchprod'
param imageTag = 'prod-latest'
param keyVaultName = 'kv-cch-dr'
param userAssignedIdentityName = 'id-cch-backend-dr'
param enableExternalIngress = true
param customDomainName = 'api-dr.cloudcontenthub.example'
param apiMinReplicas = 1
param apiMaxReplicas = 10
param workerMinReplicas = 1
param workerMaxReplicas = 15
