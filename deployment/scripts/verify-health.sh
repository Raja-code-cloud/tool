#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:?environment required (dev|qa|prod|dr)}"
RESOURCE_GROUP="rg-cch-${ENVIRONMENT}"
API_APP="ca-cch-api-${ENVIRONMENT}"

FQDN="$(az containerapp show \
  --name "$API_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv)"

if [[ -z "$FQDN" ]]; then
  echo "Unable to resolve ingress FQDN for ${API_APP}" >&2
  exit 1
fi

BASE_URL="https://${FQDN}"
echo "Verifying health endpoints at ${BASE_URL}"

curl --fail --silent --show-error --max-time 10 "${BASE_URL}/health/live" >/dev/null
curl --fail --silent --show-error --max-time 10 "${BASE_URL}/health/ready" >/dev/null

echo "Health verification succeeded for ${ENVIRONMENT}"
