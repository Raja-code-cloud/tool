#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:?environment required (dev|qa|prod|dr)}"
REVISION_NAME="${2:?revision name required}"
RESOURCE_GROUP="rg-cch-${ENVIRONMENT}"
API_APP="ca-cch-api-${ENVIRONMENT}"

echo "Rolling back ${API_APP} in ${ENVIRONMENT} to revision ${REVISION_NAME}"

az containerapp revision activate \
  --name "$API_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --revision "$REVISION_NAME" \
  --output none

echo "Rollback activated for API revision ${REVISION_NAME}"
