#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:?environment required (dev|qa|prod|dr)}"
IMAGE_TAG="${2:?image tag required}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PARAM_FILE="${ROOT_DIR}/infra/container-apps/bicep/parameters/${ENVIRONMENT}.bicepparam"
RESOURCE_GROUP="rg-cch-${ENVIRONMENT}"

if [[ ! -f "$PARAM_FILE" ]]; then
  echo "Missing parameter file: $PARAM_FILE" >&2
  exit 1
fi

echo "Deploying backend to ${ENVIRONMENT} with image tag ${IMAGE_TAG}"

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "${ROOT_DIR}/infra/container-apps/bicep/main.bicep" \
  --parameters "$PARAM_FILE" \
  --parameters imageTag="$IMAGE_TAG"

API_APP="ca-cch-api-${ENVIRONMENT}"
WORKER_APP="ca-cch-worker-${ENVIRONMENT}"
BEAT_APP="ca-cch-beat-${ENVIRONMENT}"
REGISTRY="${ACR_LOGIN_SERVER:?ACR_LOGIN_SERVER is required}"

for app in "$API_APP" "$WORKER_APP" "$BEAT_APP"; do
  image_repo="cloud-content-hub-api"
  if [[ "$app" != "$API_APP" ]]; then
    image_repo="cloud-content-hub-worker"
  fi
  az containerapp update \
    --name "$app" \
    --resource-group "$RESOURCE_GROUP" \
    --image "${REGISTRY}/${image_repo}:${IMAGE_TAG}" \
    --output none
done

MIGRATION_JOB="caj-cch-migrate-${ENVIRONMENT}"
echo "Starting migration job ${MIGRATION_JOB}"
az containerapp job start \
  --name "$MIGRATION_JOB" \
  --resource-group "$RESOURCE_GROUP" \
  --output none

echo "Deployment completed for ${ENVIRONMENT}"
