#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:?environment required (local|dev|qa|prod|dr)}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "$ENVIRONMENT" == "local" ]]; then
  docker compose \
    -f "${ROOT_DIR}/docker/docker-compose.yml" \
    --profile tools \
    run --rm migrate
  exit 0
fi

RESOURCE_GROUP="rg-cch-${ENVIRONMENT}"
MIGRATION_JOB="caj-cch-migrate-${ENVIRONMENT}"

az containerapp job start \
  --name "$MIGRATION_JOB" \
  --resource-group "$RESOURCE_GROUP" \
  --output none

echo "Migration job started for ${ENVIRONMENT}"
