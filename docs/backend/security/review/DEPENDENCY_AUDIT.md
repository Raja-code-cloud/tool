# Dependency Audit Report

Review date: 2026-08-02  
Project: `backend/pyproject.toml`  
Python: 3.13

## Scan Methods

| Tool        | Command              | Scope                           | Result                     |
| ----------- | -------------------- | ------------------------------- | -------------------------- |
| pip-audit   | `pip-audit .`        | Project isolated venv           | **0 vulnerabilities**      |
| pip-audit   | `pip-audit` (global) | System/site-packages            | 91 findings in 19 packages |
| Safety      | Not run              | Requires API key / network auth | Skipped                    |
| OSV-Scanner | Not installed        | —                               | Skipped                    |

## pip-audit — Project Scope (Authoritative)

```
cd backend
pip-audit .
```

**Result:** No known vulnerabilities found in the resolved project dependency tree.

This scan uses an isolated virtual environment resolving only `pyproject.toml` direct dependencies and their transitive requirements.

## pip-audit — Global Environment (Informational)

A scan of the system Python environment reported vulnerabilities in packages **not declared as direct backend dependencies**, including:

| Package            | Installed | Notes                                               |
| ------------------ | --------- | --------------------------------------------------- |
| aiohttp            | 3.13.5    | Transitive of other tools; fix 3.14.x               |
| cryptography       | 46.0.3    | Direct dep `>=44.0`; upgrade to ≥46.0.6 recommended |
| PyJWT              | 2.12.1    | Direct dep `>=2.10`; upgrade to ≥2.13.0 recommended |
| pillow, lxml, etc. | Various   | Dev/tooling packages outside backend runtime        |

**Action:** CI should run `pip-audit .` against the project venv only, not the global interpreter.

## Direct Runtime Dependencies Review

| Package             | Declared | Security relevance                                 |
| ------------------- | -------- | -------------------------------------------------- |
| PyJWT[crypto]       | ≥2.10    | JWT signing/verification — pin ≥2.13.0             |
| cryptography        | ≥44.0    | Key operations — pin ≥46.0.6                       |
| authlib             | ≥1.4     | OAuth token exchange                               |
| fastapi             | ≥0.115   | HTTP delivery                                      |
| httpx               | ≥0.28    | Outbound HTTP (duplicate entry — remove duplicate) |
| azure-identity      | ≥1.19    | Managed identity / SP auth                         |
| azure-storage-blob  | ≥12.24   | Blob storage and SAS                               |
| celery[redis]       | ≥5.4     | Background tasks                                   |
| redis               | ≥5.2     | Cache, DLQ, rate-limit future                      |
| sqlalchemy[asyncio] | ≥2.0     | ORM — parameterized queries                        |
| structlog           | ≥24.4    | Structured logging                                 |
| uvicorn[standard]   | ≥0.34    | ASGI server                                        |

## Supply Chain Gaps

| Gap                     | Risk   | Recommendation                                                 |
| ----------------------- | ------ | -------------------------------------------------------------- |
| No lockfile             | Medium | Generate `requirements.lock` or adopt uv/poetry lock           |
| No hash pinning         | Medium | Enable `--require-hashes` in CI                                |
| No SBOM                 | Low    | Generate CycloneDX SBOM in CI                                  |
| Duplicate httpx         | Low    | Remove duplicate line in pyproject.toml                        |
| pytest-benchmark filter | Low    | Install pytest-benchmark in dev or remove filterwarnings entry |

## Recommended CI Gate

```yaml
- name: Dependency audit
  run: |
    cd backend
    pip install pip-audit
    pip-audit .
```

## Upgrade Priority

1. **PyJWT** → 2.13.0+ (token handling CVEs)
2. **cryptography** → 46.0.7+ (OpenSSL-related advisories)
3. Establish lockfile and repeat audit on every release branch

## Secrets Scan

Manual review: no `.env` files with production secrets committed.  
`backend/.env.example` contains development placeholders only — must not be reused in production.
