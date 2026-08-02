# Authentication Architecture

## Purpose

The identity infrastructure under `backend/src/cloud_content_hub/infrastructure/identity/` implements provider-agnostic authentication, token management, and authorization primitives. Application and domain layers depend only on interfaces and neutral models such as `Principal`, `UnifiedIdentity`, and `IdentityProvider`.

## Components

| Component                           | Responsibility                                     |
| ----------------------------------- | -------------------------------------------------- |
| `interfaces/identity_provider.py`   | Provider contract                                  |
| `providers/`                        | Entra, Google, mock, and placeholder adapters      |
| `factory.py` / `registry.py`        | Composition and lookup                             |
| `jwt.py` / `tokens.py`              | Application JWT issue/verify and session lifecycle |
| `claims.py`                         | Provider claim normalization                       |
| `principal.py`                      | Request-scoped authenticated actor                 |
| `rbac.py` / `permissions.py`        | Role and permission evaluation                     |
| `middleware.py` / `dependencies.py` | HTTP extraction and FastAPI dependencies           |
| `health.py`                         | Provider health aggregation                        |

## Flow

1. A client starts OAuth through a registered provider (`authenticate`).
2. The provider callback exchanges the authorization code (`exchange_code`).
3. External ID token claims are mapped to `UnifiedIdentity`.
4. The application issues its own access/refresh JWT pair (`TokenService`).
5. Subsequent requests present the access token; middleware resolves a `Principal`.
6. Route dependencies enforce roles and permissions.

## Boundaries

- Infrastructure owns provider SDK usage, JWKS retrieval, OAuth mechanics, and JWT cryptography.
- Application services consume `Principal` and RBAC utilities; they never read raw provider claims.
- Business use cases such as user registration, workspace membership, and session persistence belong in application modules and repositories.

## Extension

Add a provider by implementing `IdentityProvider`, registering it in `IdentityFactory.build_registry()`, and documenting claim mapping. Application code remains unchanged.
