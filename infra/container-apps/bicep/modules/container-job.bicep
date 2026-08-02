param name string
param location string
param tags object
param environmentId string
param acrLoginServer string
param acrResourceId string
param identityId string
param image string
param command array
param args array
param secrets array
param env array

resource containerJob 'Microsoft.App/jobs@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identityId}': {}
    }
  }
  properties: {
    environmentId: environmentId
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 1800
      replicaRetryLimit: 1
      registries: [
        {
          server: acrLoginServer
          identity: identityId
        }
      ]
      secrets: [for secret in secrets: {
        name: secret.name
        keyVaultUrl: secret.keyVaultUrl
        identity: identityId
      }]
    }
    template: {
      containers: [
        {
          name: 'migrate'
          image: image
          command: command
          args: args
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [for variable in env: contains(variable, 'secretRef') ? {
            name: variable.name
            secretRef: variable.secretRef
          } : {
            name: variable.name
            value: string(variable.value)
          }]
        }
      ]
    }
  }
}

output jobName string = containerJob.name
