# Azure Container Apps

Infrastructure is defined in `infra/container-apps/bicep/`.

## Topology

```text
Azure Container Apps Environment
├── ca-cch-api-<env>        (ingress, HTTP scaling)
├── ca-cch-worker-<env>     (internal, CPU scaling)
├── ca-cch-beat-<env>       (internal, fixed 1 replica)
└── caj-cch-migrate-<env>   (manual migration job)
```

Shared platform dependencies (outside this module):

- Azure Container Registry
- Azure Key Vault
- Log Analytics workspace
- Azure Database for PostgreSQL 17
- Azure Cache for Redis
- Azure Blob Storage

## Bicep modules

| File                          | Purpose                                        |
| ----------------------------- | ---------------------------------------------- |
| `main.bicep`                  | Environment orchestration                      |
| `modules/container-app.bicep` | Reusable ACA app with ingress, probes, secrets |
| `modules/container-job.bicep` | Manual migration job                           |
| `parameters/*.bicepparam`     | Environment-specific values                    |

## Deploy

```bash
az deployment group create \
  --resource-group rg-cch-dev \
  --template-file infra/container-apps/bicep/main.bicep \
  --parameters infra/container-apps/bicep/parameters/dev.bicepparam \
  --parameters imageTag=<git-sha>
```

## Ingress and scaling

**API**

- External HTTPS ingress on port 8000
- HTTP concurrency scaling (default threshold: 100 concurrent requests)
- Min/max replicas configured per environment parameter file

**Worker**

- No ingress
- CPU utilization scaling

**Beat**

- Fixed single replica (`minReplicas = maxReplicas = 1`)

## Health probes

Probes target implemented application routes:

| Probe     | Path            | Purpose                      |
| --------- | --------------- | ---------------------------- |
| Liveness  | `/health/live`  | Process alive                |
| Readiness | `/health/ready` | PostgreSQL + Redis available |

These are the canonical routes. Legacy aliases `/live` and `/ready` remain available
for backwards compatibility and return identical responses (excluded from OpenAPI).
See `backend/src/cloud_content_hub/api/routers/v1/health.py`.

## Secrets

Container Apps secrets reference Key Vault URLs:

- `CCH-DATABASE-URL` — API/worker runtime role
- `CCH-MIGRATION-DATABASE-URL` — migration job only
- `CCH-REDIS-URL` — broker/backend

User-assigned managed identity pulls images from ACR and resolves Key Vault secrets.

## Identity and registry

Each environment provisions `id-cch-backend-<env>` with:

- `AcrPull` on the target registry
- Key Vault secret GET permissions

## Environment parameters

| Parameter file    | Region (default) | Notes                           |
| ----------------- | ---------------- | ------------------------------- |
| `dev.bicepparam`  | eastus           | Lower replica bounds            |
| `qa.bicepparam`   | eastus           | Pre-production                  |
| `prod.bicepparam` | eastus           | Custom domain, higher scale     |
| `dr.bicepparam`   | westus2          | DR region, shared prod registry |

Replace subscription IDs, workspace IDs, and domain names before first deploy.

## Disaster recovery

DR reuses production registry images with independent ACA environment, Key Vault, PostgreSQL replica/failover target, and Redis in the DR region. Traffic failover is handled at DNS/global load balancing outside this module.
