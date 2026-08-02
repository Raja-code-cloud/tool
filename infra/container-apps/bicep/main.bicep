@description('Cloud Content Hub backend on Azure Container Apps')
param location string = resourceGroup().location
param environmentName string
param workloadProfile string = 'Consumption'
param logAnalyticsWorkspaceId string
param containerAppsEnvironmentId string = ''
param acrLoginServer string
param acrResourceId string
param imageTag string
param apiImageRepository string = 'cloud-content-hub-api'
param workerImageRepository string = 'cloud-content-hub-worker'
param apiMinReplicas int = 1
param apiMaxReplicas int = 10
param workerMinReplicas int = 1
param workerMaxReplicas int = 20
param beatMinReplicas int = 1
param beatMaxReplicas int = 1
param enableExternalIngress bool = true
param customDomainName string = ''
param keyVaultName string
param userAssignedIdentityName string

var tags = {
  application: 'cloud-content-hub'
  component: 'backend'
  environment: environmentName
}

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: userAssignedIdentityName
  location: location
  tags: tags
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' existing = if (containerAppsEnvironmentId != '') {
  name: last(split(containerAppsEnvironmentId, '/'))
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = if (containerAppsEnvironmentId == '') {
  name: 'cae-cch-${environmentName}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceId, '2023-09-01').primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: workloadProfile
        workloadProfileType: workloadProfile
      }
    ]
  }
}

var environmentResourceId = containerAppsEnvironmentId != '' ? containerAppsEnvironmentId : managedEnvironment.id

module apiApp 'modules/container-app.bicep' = {
  name: 'cch-api-${environmentName}'
  params: {
    name: 'ca-cch-api-${environmentName}'
    location: location
    tags: tags
    environmentId: environmentResourceId
    acrLoginServer: acrLoginServer
    acrResourceId: acrResourceId
    identityId: userAssignedIdentity.id
    image: '${acrLoginServer}/${apiImageRepository}:${imageTag}'
    targetPort: 8000
    ingressExternal: enableExternalIngress
    customDomainName: customDomainName
    minReplicas: apiMinReplicas
    maxReplicas: apiMaxReplicas
    cpu: '1.0'
    memory: '2Gi'
    command: []
    args: []
    probes: [
      {
        type: 'Liveness'
        httpGet: {
          path: '/health/live'
          port: 8000
        }
        initialDelaySeconds: 10
        periodSeconds: 30
        failureThreshold: 3
      }
      {
        type: 'Readiness'
        httpGet: {
          path: '/health/ready'
          port: 8000
        }
        initialDelaySeconds: 15
        periodSeconds: 15
        failureThreshold: 5
      }
    ]
    secrets: [
      { name: 'database-url', keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/secrets/CCH-DATABASE-URL' }
      { name: 'redis-url', keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/secrets/CCH-REDIS-URL' }
    ]
    env: [
      { name: 'CCH_ENVIRONMENT', value: environmentName == 'prod' || environmentName == 'dr' ? 'production' : 'staging' }
      { name: 'CCH_SERVICE_VERSION', value: imageTag }
      { name: 'CCH_LOG_LEVEL', value: 'INFO' }
      { name: 'CCH_OPENAPI_ENABLED', value: string(environmentName != 'prod' && environmentName != 'dr') }
      { name: 'CCH_DATABASE_URL', secretRef: 'database-url' }
      { name: 'CCH_REDIS_URL', secretRef: 'redis-url' }
      { name: 'CCH_HTTP_ALLOWED_ORIGINS', value: '["https://app.example.com"]' }
      { name: 'CCH_AZURE_STORAGE_ACCOUNT_URL', value: 'https://storage.example.blob.core.windows.net' }
      { name: 'PORT', value: '8000' }
    ]
  }
}

module workerApp 'modules/container-app.bicep' = {
  name: 'cch-worker-${environmentName}'
  params: {
    name: 'ca-cch-worker-${environmentName}'
    location: location
    tags: tags
    environmentId: environmentResourceId
    acrLoginServer: acrLoginServer
    acrResourceId: acrResourceId
    identityId: userAssignedIdentity.id
    image: '${acrLoginServer}/${workerImageRepository}:${imageTag}'
    targetPort: 0
    ingressExternal: false
    customDomainName: ''
    minReplicas: workerMinReplicas
    maxReplicas: workerMaxReplicas
    cpu: '1.0'
    memory: '2Gi'
    command: []
    args: []
    probes: []
    secrets: [
      { name: 'database-url', keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/secrets/CCH-DATABASE-URL' }
      { name: 'redis-url', keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/secrets/CCH-REDIS-URL' }
    ]
    env: [
      { name: 'CCH_ENVIRONMENT', value: environmentName == 'prod' || environmentName == 'dr' ? 'production' : 'staging' }
      { name: 'CCH_SERVICE_VERSION', value: imageTag }
      { name: 'CCH_LOG_LEVEL', value: 'INFO' }
      { name: 'CCH_DATABASE_URL', secretRef: 'database-url' }
      { name: 'CCH_REDIS_URL', secretRef: 'redis-url' }
      { name: 'CELERY_CONCURRENCY', value: '4' }
    ]
  }
}

module beatApp 'modules/container-app.bicep' = {
  name: 'cch-beat-${environmentName}'
  params: {
    name: 'ca-cch-beat-${environmentName}'
    location: location
    tags: tags
    environmentId: environmentResourceId
    acrLoginServer: acrLoginServer
    acrResourceId: acrResourceId
    identityId: userAssignedIdentity.id
    image: '${acrLoginServer}/${workerImageRepository}:${imageTag}'
    targetPort: 0
    ingressExternal: false
    customDomainName: ''
    minReplicas: beatMinReplicas
    maxReplicas: beatMaxReplicas
    cpu: '0.5'
    memory: '1Gi'
    command: ['celery']
    args: ['--app', 'cloud_content_hub.workers.runtime:celery_app', 'beat', '--loglevel', 'INFO', '--schedule', '/tmp/celerybeat-schedule']
    probes: []
    secrets: [
      { name: 'redis-url', keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/secrets/CCH-REDIS-URL' }
    ]
    env: [
      { name: 'CCH_ENVIRONMENT', value: environmentName == 'prod' || environmentName == 'dr' ? 'production' : 'staging' }
      { name: 'CCH_SERVICE_VERSION', value: imageTag }
      { name: 'CCH_LOG_LEVEL', value: 'INFO' }
      { name: 'CCH_REDIS_URL', secretRef: 'redis-url' }
    ]
  }
}

module migrationJob 'modules/container-job.bicep' = {
  name: 'cch-migrate-${environmentName}'
  params: {
    name: 'caj-cch-migrate-${environmentName}'
    location: location
    tags: tags
    environmentId: environmentResourceId
    acrLoginServer: acrLoginServer
    acrResourceId: acrResourceId
    identityId: userAssignedIdentity.id
    image: '${acrLoginServer}/${apiImageRepository}:${imageTag}'
    command: ['alembic']
    args: ['upgrade', 'head']
    secrets: [
      { name: 'migration-database-url', keyVaultUrl: 'https://${keyVaultName}.vault.azure.net/secrets/CCH-MIGRATION-DATABASE-URL' }
    ]
    env: [
      { name: 'CCH_ENVIRONMENT', value: environmentName == 'prod' || environmentName == 'dr' ? 'production' : 'staging' }
      { name: 'CCH_DATABASE_URL', secretRef: 'migration-database-url' }
    ]
  }
}

output apiFqdn string = apiApp.outputs.fqdn
output apiAppName string = apiApp.outputs.appName
output workerAppName string = workerApp.outputs.appName
output beatAppName string = beatApp.outputs.appName
output migrationJobName string = migrationJob.outputs.jobName
output managedIdentityPrincipalId string = userAssignedIdentity.properties.principalId
