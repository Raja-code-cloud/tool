#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-local}"
IMAGE_TAG="${2:-local}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ "$ENVIRONMENT" == "local" ]]; then
  docker compose \
    -f "${ROOT_DIR}/docker/docker-compose.yml" \
    build \
    --build-arg VCS_REF="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || echo local)" \
    --build-arg BUILD_DATE="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  exit 0
fi

REGISTRY="${ACR_LOGIN_SERVER:?ACR_LOGIN_SERVER is required}"
docker buildx build \
  --file "${ROOT_DIR}/docker/Dockerfile" \
  --target runtime \
  --tag "${REGISTRY}/cloud-content-hub-api:${IMAGE_TAG}" \
  --push \
  "${ROOT_DIR}"

docker buildx build \
  --file "${ROOT_DIR}/docker/Dockerfile.worker" \
  --target runtime \
  --tag "${REGISTRY}/cloud-content-hub-worker:${IMAGE_TAG}" \
  --push \
  "${ROOT_DIR}"

echo "Built and pushed images for ${ENVIRONMENT}:${IMAGE_TAG}"
