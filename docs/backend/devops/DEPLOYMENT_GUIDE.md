# Deployment Guide

Cloud Content Hub backend deployments are immutable: build once, promote the same container image through environments, and change behavior only through typed `CCH_*` configuration and Azure secret references.

## Deployable units

| Unit    | Image                      | Purpose                           |
| ------- | -------------------------- | --------------------------------- |
| API     | `cloud-content-hub-api`    | FastAPI HTTP ingress              |
| Worker  | `cloud-content-hub-worker` | Celery task processing            |
| Beat    | `cloud-content-hub-worker` | Celery scheduler (single replica) |
| Migrate | `cloud-content-hub-api`    | Alembic upgrade job               |

## Environments

| Environment | Purpose                   | Compose / IaC                                          |
| ----------- | ------------------------- | ------------------------------------------------------ |
| local       | Developer workstation     | `docker/docker-compose.yml` + `docker-compose.dev.yml` |
| dev         | Shared development        | Azure Container Apps + `parameters/dev.bicepparam`     |
| qa          | Pre-production validation | Azure Container Apps + `parameters/qa.bicepparam`      |
| prod        | Production                | Azure Container Apps + `parameters/prod.bicepparam`    |
| dr          | Disaster recovery         | Azure Container Apps + `parameters/dr.bicepparam`      |

## Local bootstrap

```bash
cp docker/.env.example docker/.env
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build
docker compose -f docker/docker-compose.yml --profile tools run --rm migrate
```

API: `http://localhost:8000`

Health probes use implemented routes:

- Liveness: `/health/live`
- Readiness: `/health/ready`

## Azure deployment flow

1. Build and push images to Azure Container Registry.
2. Deploy Bicep (`infra/container-apps/bicep/main.bicep`) to the target resource group.
3. Run the migration Container Apps Job.
4. Update API, worker, and beat revisions to the new image tag.
5. Verify `/health/live` and `/health/ready`.

```bash
export ACR_LOGIN_SERVER=acrcchdev.azurecr.io
deployment/scripts/build-images.sh dev <git-sha>
deployment/scripts/deploy.sh dev <git-sha>
deployment/scripts/verify-health.sh dev
```

## GitHub Actions

- `backend-ci.yml`: lint, typing, unit tests, integration tests, Docker build smoke.
- `backend-cd.yml`: build/push to ACR, deploy/rollback to ACA, health verification.
- `security-scan.yml`: pip-audit, gitleaks, Trivy, SBOM, cosign hook.
- `dependency-update.yml`: weekly dependency lock refresh PR.

## Required repository secrets / variables

**Secrets**

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

**Variables**

- `ACR_NAME`
- `ACR_LOGIN_SERVER`

Key Vault secrets (per environment):

- `CCH-DATABASE-URL`
- `CCH-MIGRATION-DATABASE-URL`
- `CCH-REDIS-URL`

## Promotion rules

- Same image digest/tag promoted from dev → qa → prod.
- Migrations run before traffic cutover.
- Production disables OpenAPI (`CCH_OPENAPI_ENABLED=false`).
- Rollback uses prior ACA revision; see `ROLLBACK.md`.

## Out of scope

This guide covers infrastructure only. Application features, repositories, services, and authentication are implemented elsewhere.
