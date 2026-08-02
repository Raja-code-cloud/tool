param name string
param location string
param tags object
param environmentId string
param acrLoginServer string
param acrResourceId string
param identityId string
param image string
param targetPort int
param ingressExternal bool
param customDomainName string
param minReplicas int
param maxReplicas int
param cpu string
param memory string
param command array
param args array
param probes array
param secrets array
param env array

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
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
    managedEnvironmentId: environmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: targetPort > 0 ? {
        external: ingressExternal
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
        customDomains: customDomainName != '' ? [
          {
            name: customDomainName
            bindingType: 'Disabled'
          }
        ] : []
      } : null
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
          name: 'app'
          image: image
          command: length(command) > 0 ? command : null
          args: length(args) > 0 ? args : null
          resources: {
            cpu: json(cpu)
            memory: memory
          }
          env: [for variable in env: contains(variable, 'secretRef') ? {
            name: variable.name
            secretRef: variable.secretRef
          } : {
            name: variable.name
            value: string(variable.value)
          }]
          probes: length(probes) > 0 ? probes : null
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: targetPort > 0 ? [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ] : [
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

output fqdn string = targetPort > 0 ? containerApp.properties.configuration.ingress.fqdn : ''
output appName string = containerApp.name
