# CI/CD

Backend delivery is automated through GitHub Actions workflows under `.github/workflows/`.

## Pipelines

### Backend CI (`backend-ci.yml`)

Triggered on pull requests and main-branch pushes affecting `backend/` or `docker/`.

Stages:

1. **Lint and type check** — Ruff lint/format, mypy strict mode, `.env.example` key validation.
2. **Unit tests** — `pytest tests/unit` with coverage artifact upload.
3. **Integration tests** — `docker compose -f docker/docker-compose.test.yml`.
4. **Docker build smoke** — build API/worker images and verify `/health/live`.

### Backend CD (`backend-cd.yml`)

Triggered manually or by `backend-v*` tags.

Stages:

1. Resolve target environment and image tag.
2. Build and push API/worker images to ACR.
3. Generate SBOM artifacts.
4. Deploy with `deployment/scripts/deploy.sh` or rollback with `rollback.sh`.
5. Verify health with `verify-health.sh`.

GitHub Environments: `backend-dev`, `backend-qa`, `backend-prod`, `backend-dr`.

### Security scan (`security-scan.yml`)

- `pip-audit` dependency scanning
- `gitleaks` secret scanning
- Trivy container scanning (CRITICAL/HIGH fail gate)
- SBOM generation via Anchore
- Cosign signing hook on release tags

### Dependency update (`dependency-update.yml`)

Weekly scheduled lockfile refresh PR with pip-audit validation.

## Quality gates

Aligned with `docs/backend/TESTING_GUIDELINES.md`:

| Gate            | Tool                |
| --------------- | ------------------- |
| Lint            | Ruff                |
| Types           | mypy strict         |
| Unit tests      | pytest              |
| Integration     | Compose test stack  |
| Container build | Docker Buildx       |
| Dependency CVEs | pip-audit           |
| Secrets         | gitleaks            |
| Container CVEs  | Trivy               |
| SBOM            | anchore/sbom-action |

## Immutable artifacts

- Images tagged with Git SHA and environment alias (`<env>-latest`).
- Production compose requires image digests (`docker-compose.prod.yml`).
- SBOM uploaded per build for supply-chain traceability.

## Rollback integration

CD workflow accepts optional `rollback_revision` input. When set, build/push is skipped and `deployment/scripts/rollback.sh` activates a prior ACA revision.

## Frontend coexistence

Existing frontend workflows (`ci.yml`, `build.yml`, `release.yml`) remain unchanged. Backend workflows are path-filtered to avoid unnecessary runs.
