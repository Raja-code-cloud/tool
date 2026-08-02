# Delivery Layer Overview

The HTTP delivery layer lives under `backend/src/cloud_content_hub/api/` and implements the public REST v1 contract documented in `docs/backend/api/`.

## Responsibilities

The delivery layer is intentionally thin:

1. Validate transport input (headers, query params, multipart, JSON bodies).
2. Resolve authentication, workspace scope, and permission dependencies.
3. Invoke exactly one application handler per endpoint.
4. Map the handler response DTO into the v1 success envelope.
5. Map application and identity exceptions to RFC 9457-compatible problem details.

No business rules, ORM access, repository calls, or provider integrations belong here.

## Layout

```
api/
├── dependencies.py      # ActorContext, workspace, auth, handler registry
├── responses.py         # Success envelope helpers
├── errors.py            # RFC 9457 + v1 failure envelope
├── openapi.py           # OpenAPI 3.1 customization
├── pagination.py        # Cursor encode/decode
├── routers/v1/          # Versioned HTTP routers
│   ├── assets.py
│   ├── content.py
│   ├── publishing.py
│   ├── scheduler.py
│   ├── analytics.py
│   ├── notifications.py
│   ├── administration.py
│   ├── health.py
│   └── router.py
└── schemas/transport.py # OpenAPI-only request models
```

## Response contract

All non-`204` successes return:

```json
{
  "success": true,
  "message": "Assets retrieved.",
  "data": {},
  "meta": {
    "requestId": "req_01",
    "page": { "nextCursor": null, "hasMore": false, "limit": 25 }
  }
}
```

Collections place pagination exclusively under `meta.page`.

## Handler wiring

Handlers are resolved from `app.state.handlers`, a `HandlerRegistry` keyed by handler name (for example `get_asset`, `list_assets`). In production the composition root in `bootstrap/handlers.py` wires real handlers from the process container. Unit tests inject mocked handlers through the registry.

## Authentication and workspace

- Bearer JWT validation is performed by `AuthenticationMiddleware`.
- Workspace-scoped routes require `X-Workspace-ID`.
- `ActorContext` is built in `dependencies.py` from the authenticated principal and workspace header.
- Permission checks use `require_permission()` from the identity infrastructure.

## Out of scope

Repositories, SQLAlchemy, Celery workers, AI/storage providers, and business logic remain in lower layers.
